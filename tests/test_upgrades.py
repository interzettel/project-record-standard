"""Exercises release comparison against disposable actual host bytes."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

from project_record.agents import install_skills
from project_record.core import RecordError
from project_record.pins import capture_pin
from project_record.upgrades import assess_upgrade


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.host = self.root / 'host'
        self.host.mkdir()
        self.old = self.release('0.4.1', 'a', None, [])
        self.kit = self.root / 'kit-a'
        import shutil
        shutil.copytree(self.kit, self.host / 'custom/prs')
        install_skills(self.kit, self.host, apply=True)
        (self.host / 'notes').mkdir()
        (self.host / 'notes/policy.md').write_text('locally authored rule\n')
        (self.host / 'records.json').write_text('{"ids":["W1","W2"],"dependsOn":{"W2":["W1"]},"accepted":true,"done":1,"total":2,"release":"host1"}')
        self.change = {'id':'RULE-1','kind':'mandatory','dimension':'records',
                       'summary':'Synthetic rule requires host review, not copying a template',
                       'profiles':['readme-only','host-branded','private-offline'],
                       'sources':[{'path':'migration.md','sha256':sha256(b'Synthetic migration notes\n').hexdigest()},
                                  {'path':'policy.md','sha256':sha256(b'Synthetic policy\n').hexdigest()}]}
        self.new = self.release('0.5.0','b','a'*40,[self.change])
        self.request = {'upgradeVersion':1,'installedPin':self.old['pin'],'host':str(self.host),
                        'hostVersion':'2.3.0','recordContractVersion':'0.2.0','profile':'readme-only',
                        'runtime':{},'provenance':{'sourceCommit':'a'*40,'archiveSha256':self.old['pin']['toolkit']['archiveSha256']},
                        'releases':[self.old,self.new],'coverage':{'complete':True,'source':'Synthetic complete two-release fixture'},'decisions':{}}

    def release(self,version,letter,previous,changes):
        kit=self.root/('kit-'+letter);(kit/'skills/example').mkdir(parents=True)
        (kit/'skills/example/SKILL.md').write_text('---\nname: example\ndescription: Synthetic upgrade fixture\n---\n# Example\n')
        (kit/'skills/manifest.json').write_text(json.dumps({'schemaVersion':1,'suiteVersion':version,'contractVersion':'0.2.0','skills':['example']}))
        (kit/'pyproject.toml').write_text('[project]\nname="synthetic"\nversion="'+version+'"\n')
        (kit/'policy.md').write_text('Synthetic policy\n');(kit/'migration.md').write_text('Synthetic migration notes\n')
        archive=self.root/(letter+'.zip')
        with ZipFile(archive,'w') as z:
            for p in sorted(kit.rglob('*')):
                if p.is_file():z.write(p,'kit/'+p.relative_to(kit).as_posix())
        pin=capture_pin(kit,['policy.md','migration.md'],letter*40,'custom/prs',sha256(archive.read_bytes()).hexdigest())
        return {'kind':'synthetic','pin':pin,'archive':str(archive),'archivePrefix':'kit',
                'source':'Synthetic archive authored in test','fromCommit':previous,'changes':changes,
                'review':{'reviewer':'Fixture author','source':'Synthetic source-backed catalogue'}}

    def snapshot(self):
        return {p.relative_to(self.host).as_posix():p.read_bytes() for p in self.host.rglob('*') if p.is_file()}

    def decision(self,decision='already-satisfied'):
        return {'decision':decision,'reason':'Explicit synthetic semantic review of selected host policy',
                'evidence':[{'path':'notes/policy.md','sha256':sha256((self.host/'notes/policy.md').read_bytes()).hexdigest()}]}

    def test_minor_assessment_no_guess_from_rule_prose(self):
        r=assess_upgrade(self.request)
        self.assertEqual(r['transitions'][0]['disposition'],'compatibility-assessment-required')
        self.assertEqual(r['matrix'][0]['disposition'],'blocked-unknown')
        self.assertFalse(r['applicationAuthorized']);self.assertFalse(r['written'])

    def test_already_satisfied_custom_readme_host_no_rewrite_or_extra_credit(self):
        self.request['decisions']['RULE-1']=self.decision()
        before=self.snapshot();a=assess_upgrade(self.request);b=assess_upgrade(self.request)
        self.assertEqual(a,b);self.assertEqual(before,self.snapshot())
        self.assertEqual(a['matrix'][0]['disposition'],'already-satisfied')
        self.assertEqual(a['overall'],'simulation-only')
        self.assertEqual(a['scopeDelta'],0);self.assertEqual(a['completionCredit'],0)
        self.assertFalse((self.host/'index.html').exists())
        self.assertEqual(a['dimensions']['hostVersion'],'2.3.0')

    def test_mandatory_and_optional_need_explicit_bound_judgment(self):
        self.request['decisions']['RULE-1']=self.decision('applicable-needs-change')
        self.assertEqual(assess_upgrade(self.request)['matrix'][0]['disposition'],'applicable-needs-change')
        self.request['decisions']['RULE-1']=self.decision('optional-deferred')
        with self.assertRaises(RecordError):assess_upgrade(self.request)
        self.new['changes'][0]['kind']='optional'
        self.assertEqual(assess_upgrade(self.request)['matrix'][0]['disposition'],'optional-deferred')

    def test_profile_not_applicable_keeps_host_choice(self):
        self.new['changes'][0]['profiles']=['host-branded']
        r=assess_upgrade(self.request);self.assertEqual(r['matrix'][0]['disposition'],'not-applicable')
        self.assertFalse(r['upgradeApplied'])

    def test_edited_owned_suite_and_partial_install_do_not_certify(self):
        path=self.host/'.agents/skills/example/SKILL.md';data=path.read_bytes();path.write_text('edited')
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')
        path.write_bytes(data);(self.host/'.project-record/agent-installation.json').unlink()
        self.assertEqual(assess_upgrade(self.request)['overall'],'blocked-unknown')

    def test_missing_history_catalogue_review_or_archive_is_unknown(self):
        for modify in [lambda r:r['coverage'].update(complete=False),
                       lambda r:r['releases'][1].update(fromCommit='c'*40),
                       lambda r:r['releases'][1].update(review=None),
                       lambda r:r['releases'][1].update(archive=None)]:
            with self.subTest(modify=modify):
                r=deepcopy(self.request);modify(r);self.assertEqual(assess_upgrade(r)['overall'],'blocked-unknown')

    def test_moved_archive_and_wrong_source_digest_conflict(self):
        archive=Path(self.new['archive']);archive.write_bytes(archive.read_bytes()+b'changed')
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')
        self.new=self.release('0.5.0','c','a'*40,[deepcopy(self.change)])
        self.new['changes'][0]['sources'][0]['sha256']='0'*64;self.request['releases'][1]=self.new
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')

    def test_stale_review_or_ambiguous_mapping_requires_resolution(self):
        self.request['decisions']['RULE-1']=self.decision();(self.host/'notes/policy.md').write_text('newer authored work')
        r=assess_upgrade(self.request);self.assertEqual(r['matrix'][0]['disposition'],'conflict-requires-owner')
        self.request['decisions']['RULE-1']=[self.decision(),self.decision()]
        with self.assertRaises(RecordError):assess_upgrade(self.request)

    def test_major_security_patch_prerelease_and_ordinary_patch(self):
        for version,kind,expected in [('1.0.0','mandatory','compatibility-assessment-required'),('0.4.2','security','prioritized-assessment-required'),('0.4.2','optional','patch-triage-required'),('0.5.0-alpha.1','optional','opt-in-only')]:
            with self.subTest(version=version,kind=kind):
                change=deepcopy(self.change);change['kind']=kind
                r=deepcopy(self.request);r['releases'][1]=self.release(version,'d','a'*40,[change])
                out=assess_upgrade(r);self.assertEqual(out['transitions'][0]['disposition'],expected);self.assertFalse(out['upgradeApplied'])
                import shutil
                shutil.rmtree(self.root/'kit-d')

    def test_unsupported_host_contract_and_runtime_conflict(self):
        self.request['recordContractVersion']='9.0.0'
        self.assertEqual(assess_upgrade(self.request)['overall'],'blocked-unknown')
        self.request['recordContractVersion']='0.2.0';self.request['installedPin']['runtime']={'python':{'versions':['3.12.0'],'evidence':'Synthetic support'}}
        self.request['runtime']={'python':'3.10.0'}
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')

    def test_same_release_and_published_synthetic_chain_remain_honest(self):
        self.request['releases']=[self.old];self.old['kind']='published'
        r=assess_upgrade(self.request);self.assertEqual(r['overall'],'assessment-ready');self.assertEqual(r['matrix'],[])
        self.request['releases'].append(self.new);self.request['decisions']['RULE-1']=self.decision()
        self.assertEqual(assess_upgrade(self.request)['overall'],'simulation-only')
        self.assertFalse(assess_upgrade(self.request)['publisherAuthenticated'])

    def test_host_and_release_symlinks_and_traversal_are_refused(self):
        outside=self.root/'outside';outside.write_text('secret')
        (self.host/'notes/link').symlink_to(outside)
        decision=self.decision();decision['evidence'][0]['path']='notes/link';self.request['decisions']['RULE-1']=decision
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')
        decision['evidence'][0]['path']='../outside'
        with self.assertRaises(RecordError):assess_upgrade(self.request)

    def test_fifo_source_never_opened(self):
        import os
        if not hasattr(os,'mkfifo'):self.skipTest('POSIX special file')
        path=self.host/'custom/prs/pyproject.toml';path.unlink();os.mkfifo(path)
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')

    def test_duplicate_change_or_stale_decision_is_invalid(self):
        self.new['changes'].append(deepcopy(self.change))
        with self.assertRaises(RecordError):assess_upgrade(self.request)
        self.new['changes'].pop();self.request['decisions']['NOT-IN-DELTA']=self.decision()
        with self.assertRaises(RecordError):assess_upgrade(self.request)

    def test_catalogue_changes_are_bound_to_request_digest(self):
        first=assess_upgrade(self.request)['requestSha256'];self.change['summary']='Different reviewed meaning'
        self.assertNotEqual(first,assess_upgrade(self.request)['requestSha256'])

    def test_target_runtime_support_is_assessed_separately(self):
        self.request['decisions']['RULE-1']=self.decision()
        self.new['pin']['runtime']={'python':{'versions':['3.13.0'],'evidence':'Synthetic target support'}}
        self.assertEqual(assess_upgrade(self.request)['overall'],'blocked-unknown')
        self.request['runtime']={'python':'3.12.0'}
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')

    def test_archive_native_version_cannot_be_blessed_by_wrong_pin_metadata(self):
        self.new['pin']['toolkit']['version']='0.6.0'
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')

    def test_contract_axes_cannot_disagree_or_hide_unsupported_anchor(self):
        self.request['decisions']['RULE-1']=self.decision()
        self.new['pin']['recordContractVersion']='0.1.0'
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')
        self.request['releases']=[self.old];self.request['decisions']={};self.old['pin']['recordContractVersion']='9.0.0'
        self.assertNotIn(assess_upgrade(self.request)['overall'],{'assessment-ready','simulation-only'})

    def test_archive_suite_omission_and_table_overlap_cannot_certify(self):
        self.request['decisions']['RULE-1']=self.decision()
        archive=Path(self.new['archive'])
        with ZipFile(archive,'a') as z:z.writestr('kit/skills/example/omitted.md','installer would include this')
        self.new['pin']['toolkit']['archiveSha256']=sha256(archive.read_bytes()).hexdigest()
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')
        with ZipFile(archive,'w') as z:
            for p in sorted((self.root/'kit-b').rglob('*')):
                if p.is_file():z.write(p,'kit/'+p.relative_to(self.root/'kit-b').as_posix())
        self.new['pin']['toolkit']['archiveSha256']=sha256(archive.read_bytes()).hexdigest()
        self.new['pin']['toolkit']['files']['skills/example/SKILL.md']='0'*64
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')

    def test_shared_verifier_all_selected_reads_are_bounded(self):
        path=self.host/'AGENTS.md'
        with path.open('ab') as f:f.write(b' '*(16*1024*1024+1))
        self.assertEqual(assess_upgrade(self.request)['overall'],'conflicted')

    def test_runtime_shape_and_deep_request_rejected_cleanly(self):
        self.request['runtime']=[]
        with self.assertRaises(RecordError):assess_upgrade(self.request)
        from project_record.upgrades import assess_file
        path=self.root/'deep.json';path.write_text('['*2000+'0'+']'*2000)
        with self.assertRaises(RecordError):assess_file(path)

    def test_cli_readonly_and_unknown_exit(self):
        path=self.root/'request.json';path.write_text(json.dumps(self.request));before=self.snapshot()
        p=subprocess.run([sys.executable,'-m','project_record','upgrade-assess','--request',str(path)],capture_output=True,text=True)
        self.assertEqual(p.returncode,3,p.stderr);self.assertEqual(json.loads(p.stdout)['overall'],'blocked-unknown')
        self.assertEqual(before,self.snapshot())
