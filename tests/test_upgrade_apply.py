"""Tests reviewed per-file upgrade application and conservative recovery."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import test_upgrades
from project_record.core import RecordError
from project_record.upgrades import preview_upgrade, apply_upgrade


class UpgradeApplyTests(unittest.TestCase):
    def setUp(self):
        self.f=test_upgrades.UpgradeTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.request=self.f.request;self.request['decisions']['RULE-1']=self.f.decision()
        self.host=self.f.host;self.root=self.f.root;self.journal=self.root/'journal'
        self.transforms=[{'kind':'format-json','path':'records.json','beforeSha256':sha256((self.host/'records.json').read_bytes()).hexdigest()}]
        self.guards=['records.json']
        self.plan=preview_upgrade(self.request,self.transforms,self.guards,'e'*40)
        self.grant={'planSha256':self.plan['planSha256'],'source':'Synthetic test owner grant','apply':True,'rollback':True,'allowSynthetic':True}

    def run_upgrade(self,mode='apply',**kwargs):
        return apply_upgrade(self.plan,self.grant,self.journal,mode=mode,**kwargs)

    def test_preview_changes_no_host_bytes_and_requires_separate_grant(self):
        before=self.f.snapshot();p=preview_upgrade(self.request,self.transforms,self.guards,'e'*40)
        self.assertEqual(p,self.plan);self.assertEqual(before,self.f.snapshot())
        grant=deepcopy(self.grant);grant['apply']=False
        with self.assertRaises(RecordError):apply_upgrade(p,grant,self.journal)
        self.assertFalse(self.journal.exists());self.assertFalse(p['written'])

    def test_apply_repeat_rollback_preserve_records_and_unrelated_work(self):
        before=self.f.snapshot();facts=json.loads((self.host/'records.json').read_text())
        result=self.run_upgrade();self.assertEqual(result['status'],'applied')
        self.assertEqual(result['verification']['bytes'],'selected-bytes-match')
        self.assertEqual(facts,json.loads((self.host/'records.json').read_text()))
        after=self.f.snapshot();self.assertEqual(after,self.f.snapshot());self.assertNotEqual(before,after)
        repeat=self.run_upgrade();self.assertEqual(repeat['status'],'applied');self.assertFalse(repeat['written'])
        (self.host/'new-author-note.txt').write_text('post-snapshot authored work')
        rollback=self.run_upgrade('rollback');self.assertEqual(rollback['status'],'rolled-back')
        for name,content in before.items():self.assertEqual(content,(self.host/name).read_bytes(),name)
        self.assertEqual((self.host/'new-author-note.txt').read_text(),'post-snapshot authored work')
        self.assertFalse(self.run_upgrade('rollback')['written'])
        self.assertEqual(self.run_upgrade()['status'],'rolled-back')

    def test_edited_owned_or_stale_preimage_refuses_before_any_mutation(self):
        (self.host/'.agents/skills/example/SKILL.md').write_text('later edit')
        before=self.f.snapshot()
        with self.assertRaises(RecordError):self.run_upgrade()
        self.assertEqual(before,self.f.snapshot());self.assertFalse(self.journal.exists())

    def test_ambiguous_mapping_and_unsafe_path_are_rejected(self):
        for transforms in [[*self.transforms,*self.transforms],[{'kind':'replace-text','path':'../outside','beforeSha256':None,'text':'x'}]]:
            with self.assertRaises(RecordError):preview_upgrade(self.request,transforms,self.guards,'e'*40)

    def test_guarded_source_replacement_cannot_change_authoritative_facts(self):
        t={'kind':'replace-text','path':'records.json','beforeSha256':sha256((self.host/'records.json').read_bytes()).hexdigest(),'text':'{}'}
        with self.assertRaises(RecordError):preview_upgrade(self.request,[t],self.guards,'e'*40)

    def test_plan_tamper_and_synthetic_grant_refuse(self):
        p=deepcopy(self.plan);p['producerRevision']='f'*40
        with self.assertRaises(RecordError):apply_upgrade(p,self.grant,self.journal)
        grant=deepcopy(self.grant);grant['allowSynthetic']=False
        with self.assertRaises(RecordError):apply_upgrade(self.plan,grant,self.journal)

    def test_post_upgrade_owned_edit_blocks_rollback_without_losing_any_bytes(self):
        self.run_upgrade();(self.host/'AGENTS.md').write_text((self.host/'AGENTS.md').read_text()+'\nNew authored instruction\n')
        before=self.f.snapshot()
        with self.assertRaises(RecordError):self.run_upgrade('rollback')
        self.assertEqual(before,self.f.snapshot());self.assertTrue(self.journal.exists())

    def test_new_file_collision_is_not_overwritten_and_new_files_rollback(self):
        t={'kind':'replace-text','path':'notes/new-guide.md','beforeSha256':None,'text':'reviewed addition\n'}
        p=preview_upgrade(self.request,[t],self.guards,'e'*40);g={**self.grant,'planSha256':p['planSha256']}
        (self.host/'notes/new-guide.md').write_text('local collision')
        with self.assertRaises(RecordError):apply_upgrade(p,g,self.journal)
        self.assertEqual((self.host/'notes/new-guide.md').read_text(),'local collision')
        (self.host/'notes/new-guide.md').unlink();apply_upgrade(p,g,self.journal)
        apply_upgrade(p,g,self.journal,mode='rollback');self.assertFalse((self.host/'notes/new-guide.md').exists())

    def test_changed_guard_or_archive_blocks_without_writes(self):
        (self.host/'records.json').write_text('{"new":"authored facts"}')
        before=self.f.snapshot()
        with self.assertRaises(RecordError):self.run_upgrade()
        self.assertEqual(before,self.f.snapshot())

    def test_journal_unknown_neighbor_or_corrupt_backup_is_refused(self):
        self.run_upgrade();(self.journal/'unowned.txt').write_text('do not delete')
        with self.assertRaises(RecordError):self.run_upgrade('rollback')
        self.assertTrue((self.journal/'unowned.txt').exists())

    def test_installer_receipt_and_rules_are_generated_by_existing_installer(self):
        from project_record.agents import install_skills
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder);install_skills(self.root/'kit-b',target,apply=True)
            expected=json.loads((target/'.project-record/agent-installation.json').read_text())
        self.run_upgrade()
        self.assertEqual(expected,json.loads((self.host/'.project-record/agent-installation.json').read_text()))

    def test_all_apply_and_rollback_write_boundaries_survive_process_death(self):
        # Each child exits immediately after one actual host mutation, before its phase update.
        plan_file=self.root/'plan.json';grant_file=self.root/'grant.json'
        plan_file.write_text(json.dumps(self.plan));grant_file.write_text(json.dumps(self.grant))
        count=len(self.plan['entries']);self.assertGreater(count,2)
        code='''import json,os,sys
from pathlib import Path
from project_record.upgrades import apply_upgrade
plan=json.loads(Path(sys.argv[1]).read_text());grant=json.loads(Path(sys.argv[2]).read_text())
seen=0
def checkpoint(stage):
 global seen
 if stage=='after-host-write':
  seen+=1
  if seen==int(sys.argv[5]):os._exit(87)
apply_upgrade(plan,grant,Path(sys.argv[3]),mode=sys.argv[4],_checkpoint=checkpoint)
'''
        initial=self.f.snapshot()
        for mode in ['apply','rollback']:
            for boundary in range(1,count+1):
                with self.subTest(mode=mode,boundary=boundary):
                    if mode=='rollback':self.run_upgrade()
                    p=subprocess.run([sys.executable,'-c',code,str(plan_file),str(grant_file),str(self.journal),mode,str(boundary)],capture_output=True,text=True)
                    self.assertEqual(p.returncode,87,p.stderr)
                    self.assertIn(json.loads((self.journal/'state.json').read_text())['status'],{'applying','rolling-back'})
                    result=self.run_upgrade(mode);self.assertEqual(result['status'],'applied' if mode=='apply' else 'rolled-back')
                    if mode=='apply':self.run_upgrade('rollback')
                    self.assertEqual(initial,self.f.snapshot())
                    import shutil
                    shutil.rmtree(self.journal)

    def test_unchanged_installation_input_edit_is_caught_on_resume(self):
        def interrupt(stage):
            if stage=='journal-prepared':raise RuntimeError('simulate interruption')
        with self.assertRaises(RuntimeError):self.run_upgrade(_checkpoint=interrupt)
        path=self.host/'custom/prs/policy.md';path.write_text('authored edit to unchanged file')
        before=self.f.snapshot()
        with self.assertRaises(RecordError):self.run_upgrade()
        self.assertEqual(before,self.f.snapshot())

    def test_new_toolkit_path_cannot_overwrite_unowned_collision(self):
        from zipfile import ZipFile
        self.f.new['pin']['toolkit']['files']['new.txt']=sha256(b'upstream').hexdigest()
        archive=Path(self.f.new['archive'])
        with ZipFile(archive,'a') as z:z.writestr('kit/new.txt',b'upstream')
        self.f.new['pin']['toolkit']['archiveSha256']=sha256(archive.read_bytes()).hexdigest()
        (self.host/'custom/prs/new.txt').write_text('unowned host bytes')
        with self.assertRaises(RecordError):preview_upgrade(self.request,self.transforms,self.guards,'e'*40)
        self.assertEqual((self.host/'custom/prs/new.txt').read_text(),'unowned host bytes')

    def test_duplicate_json_keys_are_not_silently_canonicalized(self):
        p=self.host/'records.json';p.write_text('{"id":"A","id":"B"}')
        t=[{'kind':'format-json','path':'records.json','beforeSha256':sha256(p.read_bytes()).hexdigest()}]
        with self.assertRaises(RecordError):preview_upgrade(self.request,t,self.guards,'e'*40)

    def test_boolean_and_number_are_distinct_guarded_source_facts(self):
        path=self.host/'records.json';text=path.read_text().replace('true','1')
        t={'kind':'replace-text','path':'records.json','beforeSha256':sha256(path.read_bytes()).hexdigest(),'text':text}
        with self.assertRaises(RecordError):preview_upgrade(self.request,[t],self.guards,'e'*40)

    def test_corrupted_journal_backup_never_overwrites_host(self):
        self.run_upgrade();p=self.journal/'state.json';value=json.loads(p.read_text())
        key=next(iter(value['before']));value['before'][key]='ZmFrZQ=='
        p.write_text(json.dumps(value));before=self.f.snapshot()
        with self.assertRaises(RecordError):self.run_upgrade('rollback')
        self.assertEqual(before,self.f.snapshot())

    def test_phase_interruptions_and_partial_rollback_are_recoverable(self):
        import shutil
        before=self.f.snapshot()
        for mode in ['apply','rollback']:
            for stage in ['journal-prepared','before-host-write','before-verification','journal-complete']:
                with self.subTest(mode=mode,stage=stage):
                    if mode=='rollback':self.run_upgrade()
                    def interrupt(actual):
                        if actual==stage:raise RuntimeError('intentional phase interruption')
                    with self.assertRaises(RuntimeError):self.run_upgrade(mode,_checkpoint=interrupt)
                    result=self.run_upgrade(mode);self.assertEqual(result['status'],'applied' if mode=='apply' else 'rolled-back')
                    if mode=='apply':self.run_upgrade('rollback')
                    self.assertEqual(before,self.f.snapshot());shutil.rmtree(self.journal)

    def test_cli_requires_explicit_mode_for_application(self):
        p=subprocess.run([sys.executable,'-m','project_record','upgrade-apply','--help'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0);self.assertIn('--mode',p.stdout)
        self.assertFalse(self.journal.exists())

    def test_historical_instruction_writer_is_preserved_for_same_release(self):
        from project_record.agents import _rules,install_skills
        pin=self.f.old['pin'];digest=sha256(_rules(pin['suite']['manifest']['skills'],pin['suite']['suiteDigest'],execution=False)).hexdigest()
        install_skills(self.root/'kit-a',self.host,apply=True,upgrade=True,rules_sha256=digest)
        pin['suite']['rulesSha256']=digest
        self.request['releases']=[self.f.old];self.request['decisions']={}
        p=preview_upgrade(self.request,self.transforms,self.guards,'e'*40)
        self.assertNotIn('AGENTS.md',[e['path'] for e in p['entries']])
        g={**self.grant,'planSha256':p['planSha256']}
        apply_upgrade(p,g,self.journal);apply_upgrade(p,g,self.journal,mode='rollback')
        self.assertEqual(sha256((self.host/'AGENTS.md').read_bytes().strip()).hexdigest(),digest)

    def test_unsupported_instruction_digest_cannot_write(self):
        from project_record.agents import install_skills
        before=self.f.snapshot()
        with self.assertRaises(RecordError):install_skills(self.root/'kit-b',self.host,apply=True,upgrade=True,rules_sha256='0'*64)
        self.assertEqual(before,self.f.snapshot())

    def test_new_suite_namespace_cannot_overwrite_unowned_host_files(self):
        from zipfile import ZipFile
        from project_record.pins import capture_pin
        kit=self.root/'kit-b';(kit/'skills/fresh').mkdir()
        (kit/'skills/fresh/SKILL.md').write_text('New upstream skill')
        m=json.loads((kit/'skills/manifest.json').read_text());m['skills'].append('fresh');(kit/'skills/manifest.json').write_text(json.dumps(m))
        archive=Path(self.f.new['archive'])
        with ZipFile(archive,'w') as z:
            for path in kit.rglob('*'):
                if path.is_file():z.write(path,'kit/'+path.relative_to(kit).as_posix())
        self.f.new['pin']=capture_pin(kit,['policy.md','migration.md'],'b'*40,'custom/prs',sha256(archive.read_bytes()).hexdigest())
        folder=self.host/'.agents/skills/fresh';folder.mkdir()
        (folder/'SKILL.md').write_text('Authored unowned host skill')
        before=self.f.snapshot()
        with self.assertRaises(RecordError):preview_upgrade(self.request,self.transforms,self.guards,'e'*40)
        self.assertEqual(before,self.f.snapshot())

    def test_dotdot_host_and_journal_aliases_are_refused(self):
        request=deepcopy(self.request);request['host']=str(self.host/'..'/'host')
        with self.assertRaises(RecordError):preview_upgrade(request,self.transforms,self.guards,'e'*40)
        (self.root/'other').mkdir();alias=self.root/'other'/'..'/'host'/'private-journal'
        before=self.f.snapshot()
        with self.assertRaises(RecordError):apply_upgrade(self.plan,self.grant,alias)
        self.assertEqual(before,self.f.snapshot())

    def test_later_independent_rollback_grant_retains_original_approval(self):
        initial={**self.grant,'rollback':False};apply_upgrade(self.plan,initial,self.journal)
        later={**self.grant,'source':'Later explicit same-plan rollback decision','apply':False}
        result=apply_upgrade(self.plan,later,self.journal,mode='rollback')
        self.assertEqual(result['status'],'rolled-back')
        self.assertEqual(result['approvalHistory'][0]['source'],initial['source'])
        self.assertEqual(result['approvalHistory'][-1]['source'],later['source'])

    def test_cooperating_processes_share_one_host_lock(self):
        plan=self.root/'lock-plan.json';grant=self.root/'lock-grant.json'
        plan.write_text(json.dumps(self.plan));grant.write_text(json.dumps(self.grant))
        code="""import json,sys
from pathlib import Path
from project_record.upgrades import apply_upgrade
p=json.loads(Path(sys.argv[1]).read_text());g=json.loads(Path(sys.argv[2]).read_text())
def pause(stage):
 if stage=='journal-prepared':
  print('locked',flush=True);sys.stdin.readline()
apply_upgrade(p,g,Path(sys.argv[3]),_checkpoint=pause)
"""
        process=subprocess.Popen([sys.executable,'-c',code,str(plan),str(grant),str(self.journal)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            self.assertEqual(process.stdout.readline().strip(),'locked')
            before=self.f.snapshot();other=self.root/'contender-journal'
            with self.assertRaises(RecordError):apply_upgrade(self.plan,self.grant,other)
            self.assertFalse(other.exists());self.assertEqual(before,self.f.snapshot())
            out,err=process.communicate('continue\n',timeout=15)
            self.assertEqual(process.returncode,0,err)
        finally:
            if process.poll() is None:process.kill();process.communicate()
        self.run_upgrade('rollback')

    def test_equivalent_double_slash_host_uses_canonical_plan_identity(self):
        if os.name=='nt':self.skipTest('POSIX double-slash alias')
        request=deepcopy(self.request);request['host']='/'+str(self.host)
        self.assertEqual(preview_upgrade(request,self.transforms,self.guards,'e'*40),self.plan)

    def test_double_slash_journal_cannot_be_hidden_inside_host(self):
        if os.name=='nt':self.skipTest('POSIX double-slash alias')
        alias=Path('/'+str(self.host/'private-journal'));before=self.f.snapshot()
        with self.assertRaises(RecordError):apply_upgrade(self.plan,self.grant,alias)
        self.assertEqual(before,self.f.snapshot())

    def test_changed_installed_skill_bytes_upgrade_and_rollback(self):
        from zipfile import ZipFile
        from project_record.pins import capture_pin
        kit=self.root/'kit-b';skill=kit/'skills/example/SKILL.md'
        skill.write_text(skill.read_text()+'\nNew reviewed instruction text\n')
        archive=Path(self.f.new['archive'])
        with ZipFile(archive,'w') as z:
            for path in kit.rglob('*'):
                if path.is_file():z.write(path,'kit/'+path.relative_to(kit).as_posix())
        self.f.new['pin']=capture_pin(kit,['policy.md','migration.md'],'b'*40,'custom/prs',sha256(archive.read_bytes()).hexdigest())
        p=preview_upgrade(self.request,self.transforms,self.guards,'e'*40);g={**self.grant,'planSha256':p['planSha256']}
        installed=self.host/'.agents/skills/example/SKILL.md';before=installed.read_bytes()
        apply_upgrade(p,g,self.journal);self.assertEqual(installed.read_bytes(),skill.read_bytes())
        apply_upgrade(p,g,self.journal,mode='rollback');self.assertEqual(installed.read_bytes(),before)

    def test_cli_preview_does_not_apply(self):
        request=self.root/'preview.json';request.write_text(json.dumps({'request':self.request,'transformations':self.transforms,'guards':self.guards,'producerRevision':'e'*40}))
        before=self.f.snapshot();p=subprocess.run([sys.executable,'-m','project_record','upgrade-preview','--request',str(request)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr);self.assertEqual(before,self.f.snapshot())
        self.assertEqual(json.loads(p.stdout)['planSha256'],self.plan['planSha256'])
