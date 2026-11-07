"""Checks actual suite distribution and the upgrade workflow's offline matrix."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from zipfile import ZipFile

import test_upgrades
from project_record.agents import install_skills
from project_record.core import RecordError
from project_record.pins import assess_update,capture_pin,_native_version
from project_record.upgrades import assess_upgrade,preview_upgrade,apply_upgrade
from tools.check_skills import check_suite

ROOT=Path(__file__).resolve().parents[1]


class UpgradeWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)

    def snapshot(self,root):
        return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*') if p.is_file()}

    def test_new_workflow_is_discoverable_and_suite_version_is_deliberate(self):
        manifest=json.loads((ROOT/'skills/manifest.json').read_text())
        self.assertIn('upgrade-project-records',manifest['skills'])
        self.assertEqual(len(manifest['skills']),12)
        self.assertEqual(_native_version(ROOT),'0.6.0-alpha.0')
        self.assertEqual(manifest['suiteVersion'],_native_version(ROOT));self.assertEqual(manifest['contractVersion'],'0.2.0')
        self.assertEqual(check_suite(ROOT)['skills'],12)

    def test_router_and_operations_separate_upgrade_from_repair(self):
        router=(ROOT/'skills/use-project-records/SKILL.md').read_text()
        operations=(ROOT/'skills/operate-project-tracking/SKILL.md').read_text()
        self.assertIn('upgrade-project-records',router);self.assertIn('upgrade-project-records',operations)
        self.assertIn('adapt-project-tracking',router)

    def test_complete_installed_distribution_repeats_and_preserves_host(self):
        host=self.root/'host';host.mkdir();(host/'AGENTS.md').write_text('# Host instructions\nKeep research sources private.\n')
        (host/'pyproject.toml').write_text('[project]\nversion="2.8.0"\n')
        original=self.snapshot(host)
        preview=install_skills(ROOT,host);self.assertFalse(preview['written']);self.assertEqual(original,self.snapshot(host))
        install_skills(ROOT,host,apply=True);receipt=json.loads((host/'.project-record/agent-installation.json').read_text())
        self.assertIn('.agents/skills/upgrade-project-records/SKILL.md',receipt['files'])
        self.assertEqual(receipt['suiteVersion'],'0.6.0-alpha.0');self.assertEqual(install_skills(ROOT,host,apply=True)['changes'],[])
        self.assertEqual((host/'pyproject.toml').read_bytes(),original['pyproject.toml'])
        self.assertTrue((host/'AGENTS.md').read_text().startswith('# Host instructions\n'))
        installed=host/'.agents/skills/upgrade-project-records/SKILL.md';installed.write_text(installed.read_text()+'\nLocally authored instruction\n')
        before=self.snapshot(host)
        with self.assertRaises(RecordError):install_skills(ROOT,host,apply=True,upgrade=True)
        self.assertEqual(before,self.snapshot(host))

    def _kit(self,name,old=False):
        kit=self.root/name;kit.mkdir();shutil.copytree(ROOT/'skills',kit/'skills')
        manifest=json.loads((kit/'skills/manifest.json').read_text())
        version='0.4.1' if old else _native_version(ROOT)
        if old:
            manifest['skills']=[n for n in manifest['skills'] if n!='upgrade-project-records']
            if (kit/'skills/upgrade-project-records').exists():shutil.rmtree(kit/'skills/upgrade-project-records')
            for name,file in [('use-project-records','baseline-router.md'),('operate-project-tracking','baseline-operations.md')]:
                shutil.copyfile(ROOT/'tests/fixtures/upgrade-workflow'/file,kit/'skills'/name/'SKILL.md')
        manifest['suiteVersion']=version;(kit/'skills/manifest.json').write_text(json.dumps(manifest))
        (kit/'pyproject.toml').write_text('[project]\nname="synthetic-workflow-kit"\nversion="'+version+'"\n')
        (kit/'migration.md').write_text('Synthetic suite addition and routing delta; source is not a published release.\n')
        archive=self.root/(name+'.zip')
        with ZipFile(archive,'w') as z:
            for p in sorted(kit.rglob('*')):
                if p.is_file():z.write(p,'kit/'+p.relative_to(kit).as_posix())
        commit=('a' if old else 'b')*40
        pin=capture_pin(kit,['migration.md','skills/manifest.json'],commit,'custom/prs',sha256(archive.read_bytes()).hexdigest())
        return kit,{'kind':'synthetic','pin':pin,'archive':str(archive),'archivePrefix':'kit','source':'Synthetic distribution fixture','fromCommit':None if old else 'a'*40,'changes':[],'review':{'reviewer':'Fixture author','source':'Actual complete suite files and migration notes inspected'}}

    def test_actual_eleven_to_twelve_skill_upgrade_interruption_and_rollback(self):
        old,anchor=self._kit('old',True);new,target=self._kit('new')
        host=self.root/'host';host.mkdir();shutil.copytree(old,host/'custom/prs');install_skills(old,host,apply=True)
        (host/'AGENTS.md').write_text('# Host-owned prefix\n'+(host/'AGENTS.md').read_text())
        (host/'records.json').write_text('{"items":[{"id":"W1","dependsOn":[]},{"id":"W2","dependsOn":["W1"]}],"accepted":true,"required":{"done":1,"total":2},"history":["kept"],"hostVersion":"2.8.0","brand":"burgundy serif"}')
        (host/'README.md').write_text('# Branded README-only research\nNo Pages.\n')
        request={'upgradeVersion':1,'installedPin':anchor['pin'],'host':str(host),'hostVersion':'2.8.0','recordContractVersion':'0.2.0','profile':'readme-only','runtime':{},'provenance':{'sourceCommit':'a'*40,'archiveSha256':anchor['pin']['toolkit']['archiveSha256']},'releases':[anchor,target],'coverage':{'complete':True,'source':'Synthetic two-release source catalogue'},'decisions':{}}
        before=self.snapshot(host);plan=preview_upgrade(request,[],['records.json'],'c'*40)
        grant={'planSha256':plan['planSha256'],'source':'Synthetic explicit suite fixture grant','apply':True,'rollback':True,'allowSynthetic':True}
        journal=self.root/'journal'
        def stop(stage):
            if stage=='after-host-write':raise RuntimeError('intentional partial distribution')
        with self.assertRaises(RuntimeError):apply_upgrade(plan,grant,journal,_checkpoint=stop)
        result=apply_upgrade(plan,grant,journal);self.assertEqual(result['status'],'applied')
        self.assertTrue((host/'.agents/skills/upgrade-project-records/SKILL.md').is_file())
        self.assertEqual(result['verification']['bytes'],'selected-bytes-match')
        self.assertFalse(apply_upgrade(plan,grant,journal)['written'])
        apply_upgrade(plan,grant,journal,mode='rollback')
        self.assertEqual(before,self.snapshot(host));self.assertFalse((host/'index.html').exists())

    def test_eight_consumer_case_and_semver_matrix(self):
        f=test_upgrades.UpgradeTests();f.setUp();self.addCleanup(f.doCleanups)
        # Cases1/2/3/4/8 use actual file evidence, not a canned classifier.
        request=f.request;request['hostVersion']='2.8.0';request['decisions']['RULE-1']=f.decision()
        before=f.snapshot();result=assess_upgrade(request)
        self.assertEqual(result['matrix'][0]['disposition'],'already-satisfied');self.assertEqual(result['dimensions']['profile'],'readme-only')
        self.assertFalse(result['applicationAuthorized']);self.assertEqual(result['completionCredit'],0);self.assertEqual(before,f.snapshot())
        request['decisions']['RULE-1']['decision']='applicable-needs-change';self.assertEqual(assess_upgrade(request)['matrix'][0]['disposition'],'applicable-needs-change')
        # Case5: edited ownership; case6: missing chain/metadata; case7: repeat.
        file=f.host/'.agents/skills/example/SKILL.md';data=file.read_bytes();file.write_text('locally authored edit')
        self.assertEqual(assess_upgrade(request)['overall'],'conflicted');file.write_bytes(data)
        request['coverage']['complete']=False;self.assertEqual(assess_upgrade(request)['overall'],'blocked-unknown')
        request['coverage']['complete']=True;self.assertEqual(assess_upgrade(request),assess_upgrade(request))
        for version,security,disposition in [('0.4.2',False,'patch-triage-required'),('0.4.2',True,'prioritized-assessment-required'),('0.5.0',False,'compatibility-assessment-required'),('1.0.0',False,'compatibility-assessment-required'),('0.6.0-alpha.0',False,'opt-in-only')]:
            with self.subTest(version=version):self.assertEqual(assess_update('0.4.1',version,security=security)['disposition'],disposition)
        request['releases'][-1]['archive']=None;self.assertEqual(assess_upgrade(request)['overall'],'blocked-unknown')
