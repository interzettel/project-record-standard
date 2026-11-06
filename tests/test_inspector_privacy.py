from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
import subprocess
import sys
import os
import unittest
from unittest.mock import patch

from project_record.core import RecordError
from project_record import inspector

ROOT=Path(__file__).resolve().parents[1]
TIME='2026-11-06T10:00:00+01:00'


def leaves(value, pointer=''):
    if isinstance(value,(dict,list)) and value:
        rows=value.items() if isinstance(value,dict) else enumerate(value)
        return [p for k,v in rows for p in leaves(v,pointer+'/'+str(k).replace('~','~0').replace('/','~1'))]
    return [pointer]


class InspectorPrivacyTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'host';self.root.mkdir()
        self.record=json.loads((ROOT/'tests/fixtures/inspector/record.json').read_text())
        for name in ['metrics','warnings','presentation','inputVisibility','supplementSources','history','deliverySummary']:
            self.record.pop(name,None)
        for row in self.record['groups']:
            row.pop('progress',None);row.pop('ledgerProgress',None)
        for row in self.record['milestones']:
            for k in ['progress','gateProgress','accepted']:row.pop(k,None)
        self.source=self.root/'safe.json';self.save_source()
        self.selection=dict(selectionVersion=1,records=[dict(id='REC',path='safe.json',kind='project-record',visibility='public')])
        self.select=self.root/'selection.json';self.select.write_text(json.dumps(self.selection))
        self.review=self.root/'review.json';self.save_review()
        self.out=Path(self.tmp.name)/'output'

    def save_source(self):
        self.source.write_text(json.dumps(self.record,indent=2)+'\n')

    def save_review(self):
        self.review.write_text(json.dumps(dict(publicReviewVersion=1,reviewer='Synthetic fixture author',decisionSource='Synthetic safe test input only',records=[dict(id='REC',sha256=sha256(self.source.read_bytes()).hexdigest(),pointers=leaves(self.record))])))

    def run_profile(self,**kwargs):
        self.assertTrue(hasattr(inspector,'inspector_profile'),'managed privacy profiles not implemented')
        return inspector.inspector_profile(self.root,self.select,self.out,observed_at=TIME,**kwargs)

    def test_private_declaration_is_refused_before_content_read(self):
        from project_record.inspector_privacy import public_model
        selection=deepcopy(self.selection);selection['records'][0]['visibility']='private'
        with patch.object(Path,'open',side_effect=AssertionError('must not read private contents')):
            with self.assertRaises(RecordError):public_model(self.root,selection,{},observed_at=TIME)

    def test_unreviewed_public_and_wrong_digest_are_refused_without_output(self):
        with self.assertRaises(RecordError):self.run_profile(audience='public',profile='host-branded',write=True)
        self.record['items'][0]['title']='Changed after review';self.save_source()
        with self.assertRaises(RecordError):self.run_profile(audience='public',profile='host-branded',review=self.review,write=True)
        self.assertFalse(self.out.exists())

    def test_public_projection_omits_unreviewed_extensions_and_selection_metadata(self):
        self.record['personalMemory']={'private':'DO-NOT-PUBLISH'}
        self.record['items'][0]['secretExtra']='DO-NOT-PUBLISH'
        self.save_source()
        review=json.loads(self.review.read_text());review['records'][0]['sha256']=sha256(self.source.read_bytes()).hexdigest();self.review.write_text(json.dumps(review))
        self.selection['records'][0].update(renderedAt='2020-01-01T00:00:00Z',producerRevision='b'*40)
        self.select.write_text(json.dumps(self.selection))
        result=self.run_profile(audience='public',profile='host-branded',review=self.review,write=True)
        page=(self.out/'index.html').read_text()
        self.assertTrue(result['publishable']);self.assertNotIn('DO-NOT-PUBLISH',page)
        self.assertNotIn('2020-01-01',page);self.assertNotIn('b'*40,page)
        self.assertNotIn('safe.json',page);self.assertIn('WORK-1',page)

    def test_every_published_leaf_needs_exact_pointer_review(self):
        review=json.loads(self.review.read_text());review['records'][0]['pointers'].remove('/items/0/title');self.review.write_text(json.dumps(review))
        with self.assertRaises(RecordError):self.run_profile(audience='public',profile='host-branded',review=self.review,write=True)

    def test_private_payload_and_unknown_public_kind_are_refused(self):
        self.record['project']['visibility']='private';self.save_source();self.save_review()
        with self.assertRaises(RecordError):self.run_profile(audience='public',profile='host-branded',review=self.review,write=True)
        self.selection['records'][0]['kind']='future';self.select.write_text(json.dumps(self.selection))
        with self.assertRaises(RecordError):self.run_profile(audience='public',profile='host-branded',review=self.review,write=True)

    def test_repeat_write_is_identical_and_check_is_read_only_and_detects_stale_bytes(self):
        first=self.run_profile(audience='owner',profile='private-offline',write=True)
        before={p.name:p.read_bytes() for p in self.out.iterdir()}
        second=self.run_profile(audience='owner',profile='private-offline',write=True)
        self.assertFalse(second['changed']);self.assertEqual(before,{p.name:p.read_bytes() for p in self.out.iterdir()})
        self.assertFalse(self.run_profile(audience='owner',profile='private-offline',check=True)['changed'])
        (self.out/'index.html').write_text('stale')
        state=self.run_profile(audience='owner',profile='private-offline',check=True)
        self.assertTrue(state['changed']);self.assertEqual(state['exitCode'],1)
        self.assertEqual((self.out/'index.html').read_text(),'stale')
        self.run_profile(audience='owner',profile='private-offline',write=True)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.out.iterdir()})

    def test_preview_no_output_and_unrelated_files_or_unowned_dirs_never_overwritten(self):
        self.assertTrue(self.run_profile(audience='owner',profile='private-offline')['changed']);self.assertFalse(self.out.exists())
        self.out.mkdir();(self.out/'index.html').write_text('authored')
        with self.assertRaises(RecordError):self.run_profile(audience='owner',profile='private-offline',write=True)
        self.assertEqual((self.out/'index.html').read_text(),'authored')

    def test_host_brand_is_safe_and_source_inputs_remain_identical(self):
        brand=self.root/'brand.json';brand.write_text(json.dumps(dict(brandVersion=1,name='Synthetic studio',font='serif',light=dict(background='#ffffff',text='#111111',link='#143484'),dark=dict(background='#111111',text='#ffffff',link='#bbcaff'))))
        before={p.name:p.read_bytes() for p in self.root.iterdir()}
        self.run_profile(audience='public',profile='host-branded',review=self.review,brand=brand,write=True)
        page=(self.out/'index.html').read_text();self.assertIn('Synthetic studio',page);self.assertIn('Georgia',page)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.root.iterdir()})
        obj=json.loads(brand.read_text());obj['light']['text']='red;}body{display:none}';brand.write_text(json.dumps(obj))
        with self.assertRaises(RecordError):self.run_profile(audience='public',profile='host-branded',review=self.review,brand=brand,check=True)

    def test_hostile_approved_text_is_inert_and_urls_are_never_activated(self):
        self.record['items'][0].update(title='</script><img src=x onerror=alert(1)>',issueUrl='javascript:alert(2)')
        self.save_source();self.save_review()
        self.run_profile(audience='public',profile='host-branded',review=self.review,write=True)
        page=(self.out/'index.html').read_text()
        self.assertNotIn('<img src=x',page);self.assertNotIn('href="javascript:',page);self.assertIn('&lt;img',page)

    def test_selected_input_collision_symlinks_and_unrelated_owned_neighbors_are_refused(self):
        self.run_profile(audience='owner',profile='private-offline',write=True)
        (self.out/'authored.txt').write_text('keep')
        with self.assertRaises(RecordError):self.run_profile(audience='owner',profile='private-offline',write=True)
        (self.out/'authored.txt').unlink()
        (self.out/'index.html').unlink();(self.out/'index.html').symlink_to(self.source)
        with self.assertRaises(RecordError):self.run_profile(audience='owner',profile='private-offline',check=True)
        self.assertEqual(json.loads(self.source.read_text()),self.record)

    def test_changed_input_and_interrupted_regeneration_stay_stale_then_recover(self):
        self.run_profile(audience='owner',profile='private-offline',write=True)
        self.record['items'][0]['title']='New source observation';self.save_source()
        self.assertEqual(self.run_profile(audience='owner',profile='private-offline',check=True)['exitCode'],1)
        from project_record.inspector_profile import _write
        calls=[]
        def interrupted(path,data):
            calls.append(path.name)
            if len(calls)==2:raise OSError('synthetic interruption')
            _write(path,data)
        with patch('project_record.inspector_profile._write',interrupted):
            with self.assertRaises(OSError):self.run_profile(audience='owner',profile='private-offline',write=True)
        self.assertEqual(self.run_profile(audience='owner',profile='private-offline',check=True)['exitCode'],1)
        self.run_profile(audience='owner',profile='private-offline',write=True)
        self.assertFalse(self.run_profile(audience='owner',profile='private-offline',check=True)['changed'])

    def test_readme_only_profile_retains_no_pages_choice_and_source_identity(self):
        from project_record.readme_profile import sync_readme
        host=Path(self.tmp.name)/'readme-host'
        shutil.copytree(ROOT/'tests/fixtures/readme-only',host)
        before={p.name:p.read_bytes() for p in host.iterdir() if p.is_file() and p.suffix=='.json'}
        r=sync_readme(host/'projects.json','readme-only',host/'README.md',host/'assets/progress.svg',write=True)
        self.assertEqual(r['metrics']['work']['total'],2)
        self.assertFalse(list(host.rglob('*.html')))
        self.assertEqual(before,{p.name:p.read_bytes() for p in host.iterdir() if p.is_file() and p.suffix=='.json'})

    def test_public_outputs_are_identical_across_process_hash_seeds(self):
        for seed in ['1','2']:
            out=Path(self.tmp.name)/('seed'+seed)
            args=[sys.executable,'-m','project_record','inspector-profile','--root',str(self.root),'--selection',str(self.select),'--output',str(out),'--observed-at',TIME,'--profile','host-branded','--audience','public','--review',str(self.review),'--write']
            result=subprocess.run(args,env={**os.environ,'PYTHONHASHSEED':seed},capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((Path(self.tmp.name)/'seed1/index.html').read_bytes()==(Path(self.tmp.name)/'seed2/index.html').read_bytes(),True)

    def test_review_brand_loader_refuses_nonregular_inputs_before_open(self):
        from project_record.inspector_profile import _load
        directory=self.root/'directory.json';directory.mkdir()
        paths=[directory]
        if hasattr(os,'mkfifo'):
            fifo=self.root/'fifo.json';os.mkfifo(fifo);paths.append(fifo)
        for path in paths:
            with self.subTest(path=path.name),patch.object(Path,'open',side_effect=AssertionError('nonregular input opened')):
                with self.assertRaises(RecordError):_load(path)

    def test_deep_review_is_controlled_refusal_and_does_not_create_output(self):
        from project_record.inspector_profile import _load
        deep=self.root/'deep.json';deep.write_text('['*20000+'0'+']'*20000)
        with self.assertRaises(RecordError):_load(deep)
        self.assertFalse(self.out.exists())

    def test_corrupted_ownership_receipt_types_cannot_authorize_writes(self):
        self.run_profile(audience='owner',profile='private-offline',write=True)
        path=self.out/'inspector-output.json';original=path.read_bytes()
        for change in [{'inspectorOutputVersion':True},{'files':['index.html']},{'files':{'index.html':'not-a-digest'}}]:
            value=json.loads(original);value.update(change);path.write_text(json.dumps(value))
            before={p.name:p.read_bytes() for p in self.out.iterdir()}
            with self.subTest(change=change),self.assertRaises(RecordError):self.run_profile(audience='owner',profile='private-offline',write=True)
            self.assertEqual(before,{p.name:p.read_bytes() for p in self.out.iterdir()})


if __name__=='__main__':unittest.main()
