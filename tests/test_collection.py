"""Exercises quiet monitoring against actual disposable installation bytes."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_upgrades
from project_record.core import RecordError
from project_record.collection import observe_releases,watch_files


class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.f=test_upgrades.UpgradeTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.root=self.f.root;self.host=self.f.host
        self.release={'version':'0.5.0','sourceCommit':'b'*40,'archiveSha256':'c'*64,'notesSha256':'d'*64,'security':False,'securitySource':None,'source':'synthetic:release/0.5.0'}
        self.request={'watchVersion':1,'consumerId':'toy-host','host':str(self.host),'pin':self.f.old['pin'],'provenance':self.f.request['provenance'],'runtime':{},'policy':{'intervalSeconds':3600,'freshnessSeconds':7200,'retrySeconds':60,'maxRetries':2,'deferrals':[]},'collection':{'attemptedAt':'2026-11-07T10:00:00Z','status':'success','source':'synthetic:collection/1','coverage':{'pagesRead':1,'pagesExpected':1},'releases':[self.release],'error':None}}
        self.now='2026-11-07T10:00:00Z'

    def observe(self,state=None,now=None):return observe_releases(self.request,now or self.now,state)

    def next_attempt(self,time='2026-11-07T11:00:00Z'):
        self.request['collection']['attemptedAt']=time;self.now=time

    def test_minor_assessment_has_sources_no_application_and_one_durable_pair(self):
        r=self.observe();self.assertEqual(len(r['notices']),1);self.assertEqual(len(r['state']['assessments']),1)
        a=next(iter(r['state']['assessments'].values()))
        self.assertEqual(a['assessment']['disposition'],'compatibility-assessment-required')
        self.assertEqual(a['release']['source'],'synthetic:release/0.5.0');self.assertFalse(r['applicationAuthorized'])
        self.assertEqual(a['status'],'attention-required');self.assertEqual(r['lastSuccess']['releaseCount'],1)

    def test_replay_is_quiet_and_does_not_refresh_observation(self):
        a=self.observe();b=self.observe(a['state'],now='2026-11-07T10:30:00Z')
        self.assertEqual(a['state'],b['state']);self.assertEqual(b['notices'],[])
        self.assertEqual(b['lastSuccess']['attemptedAt'],'2026-11-07T10:00:00Z')
        self.next_attempt();c=self.observe(b['state']);self.assertEqual(c['notices'],[])
        self.assertEqual(next(iter(c['state']['assessments'].values()))['revision'],1)

    def test_new_security_bypasses_ordinary_deferral_and_reuses_pair(self):
        self.release['version']='0.4.2';self.request['policy']['deferrals']=[{'from':'0.4.1','to':'0.4.2','reason':'Monthly review'}]
        a=self.observe();self.assertEqual(next(iter(a['state']['assessments'].values()))['assessment']['disposition'],'deferred-with-reason')
        self.next_attempt();self.release.update(security=True,securitySource='synthetic:advisory/1')
        b=self.observe(a['state']);self.assertEqual(len(b['state']['assessments']),1);self.assertEqual(len(b['notices']),1)
        self.assertEqual(next(iter(b['state']['assessments'].values()))['assessment']['disposition'],'prioritized-assessment-required')
        self.next_attempt('2026-11-07T12:00:00Z');self.release['securitySource']='synthetic:advisory/2'
        self.assertEqual(len(self.observe(b['state'])['notices']),1)

    def test_major_patch_prerelease_and_unverified_target(self):
        for version,expected in [('1.0.0','compatibility-assessment-required'),('0.4.2','patch-triage-required'),('0.6.0-alpha.0','opt-in-only')]:
            self.release['version']=version;r=self.observe();self.assertEqual(next(iter(r['state']['assessments'].values()))['assessment']['disposition'],expected)
        self.release['archiveSha256']=None;r=self.observe();self.assertEqual(next(iter(r['state']['assessments'].values()))['status'],'blocked-unknown')

    def test_partial_failed_and_unknown_pages_preserve_last_success_counts(self):
        a=self.observe();self.next_attempt();c=self.request['collection'];c.update(status='partial',releases=[],error='page2 quota');c['coverage']={'pagesRead':1,'pagesExpected':3}
        b=self.observe(a['state']);self.assertEqual(b['lastSuccess'],a['lastSuccess']);self.assertEqual(len(b['state']['assessments']),1)
        self.assertEqual(b['health'],'degraded');self.assertEqual(b['nextDue'],'2026-11-07T11:01:00Z')
        self.next_attempt('2026-11-07T11:01:00Z');c.update(status='failed',error='offline');c['coverage']={'pagesRead':0,'pagesExpected':None}
        d=self.observe(b['state']);self.assertEqual(d['lastSuccess'],a['lastSuccess'])
        self.next_attempt('2026-11-07T11:02:00Z');e=self.observe(d['state']);self.assertEqual(e['health'],'retry-exhausted');self.assertIsNone(e['nextDue'])
        self.next_attempt('2026-11-07T12:00:00Z');c.update(status='success',error=None,releases=[self.release]);c['coverage']={'pagesRead':1,'pagesExpected':1}
        self.assertEqual(self.observe(e['state'])['health'],'current')

    def test_stale_dropped_and_delayed_schedules_are_visible(self):
        a=self.observe();b=self.observe(a['state'],now='2026-11-07T13:00:00Z')
        self.assertEqual(b['health'],'stale');self.assertTrue(b['scheduleMissed']);self.assertEqual(a['state'],b['state'])
        self.next_attempt('2026-11-07T13:00:00Z');c=self.observe(a['state']);self.assertTrue(c['lateAttempt']);self.assertEqual(c['health'],'current')

    def test_changed_immutable_identity_is_conflicted_and_sticky(self):
        a=self.observe();self.next_attempt();self.release['sourceCommit']='f'*40
        b=self.observe(a['state']);entry=next(iter(b['state']['assessments'].values()));self.assertEqual(entry['status'],'conflicted');self.assertEqual(len(b['notices']),1)
        self.next_attempt('2026-11-07T12:00:00Z');self.release['sourceCommit']='b'*40
        self.assertEqual(next(iter(self.observe(b['state'])['state']['assessments'].values()))['status'],'conflicted')

    def test_real_owned_drift_keeps_assessment_unknown(self):
        (self.host/'.agents/skills/example/SKILL.md').write_text('authored edit')
        r=self.observe();self.assertEqual(r['health'],'degraded');self.assertIsNone(r['lastSuccess'])
        self.assertEqual(next(iter(r['state']['assessments'].values()))['status'],'blocked-unknown')

    def test_duplicate_releases_bad_times_and_security_without_source_refuse(self):
        r=deepcopy(self.request);r['collection']['releases'].append(deepcopy(self.release))
        with self.assertRaises(RecordError):observe_releases(r,self.now)
        with self.assertRaises(RecordError):self.observe(now='2026-11-07T09:00:00Z')
        self.release['security']=True
        with self.assertRaises(RecordError):self.observe()

    def test_conflicting_same_attempt_and_regression_are_rejected(self):
        a=self.observe();self.release['notesSha256']='e'*64
        with self.assertRaises(RecordError):self.observe(a['state'])
        self.request['collection']['attemptedAt']='2026-11-07T09:00:00Z'
        with self.assertRaises(RecordError):self.observe(a['state'])

    def test_owned_writer_preview_repeat_and_atomic_interruption(self):
        request=self.root/'watch.json';request.write_text(json.dumps(self.request));state=self.root/'watch-state'
        before=self.f.snapshot();r=watch_files(request,state,self.now);self.assertFalse(state.exists());self.assertEqual(before,self.f.snapshot())
        a=watch_files(request,state,self.now,write=True);self.assertTrue(a['written'])
        self.assertFalse(watch_files(request,state,self.now,write=True)['written'])
        self.assertEqual(before,self.f.snapshot())
        self.next_attempt();request.write_text(json.dumps(self.request));saved=(state/'state.json').read_bytes()
        with patch('project_record.collection._atomic',side_effect=OSError('simulated pre-replacement failure')):
            with self.assertRaises(OSError):watch_files(request,state,self.now,write=True)
        self.assertEqual(saved,(state/'state.json').read_bytes());self.assertTrue(watch_files(request,state,self.now,write=True)['written'])

    def test_unknown_neighbors_host_collision_and_corrupt_state_refuse(self):
        p=self.root/'watch.json';p.write_text(json.dumps(self.request));folder=self.root/'state';folder.mkdir();(folder/'keep').write_text('authored')
        with self.assertRaises(RecordError):watch_files(p,folder,self.now,write=True)
        with self.assertRaises(RecordError):watch_files(p,self.host/'state',self.now,write=True)
        (folder/'keep').unlink();(folder/'state.json').write_text('{}')
        with self.assertRaises(RecordError):watch_files(p,folder,self.now,write=True)

    def test_current_empty_complete_collection_is_distinct_from_failed_zero(self):
        self.request['collection']['releases']=[];a=self.observe();self.assertEqual(a['lastSuccess']['releaseCount'],0)
        self.next_attempt();self.request['collection'].update(status='failed',error='offline')
        b=self.observe(a['state']);self.assertEqual(b['lastSuccess'],a['lastSuccess'])

    def test_unknown_identity_is_anchored_when_first_observed(self):
        self.release.update(sourceCommit=None,archiveSha256=None);a=self.observe()
        self.next_attempt();self.release.update(sourceCommit='b'*40,archiveSha256='c'*64);b=self.observe(a['state'])
        self.next_attempt('2026-11-07T12:00:00Z');self.release['sourceCommit']='f'*40
        self.assertEqual(next(iter(self.observe(b['state'])['state']['assessments'].values()))['status'],'conflicted')

    def test_historical_releases_do_not_prompt_downgrades(self):
        for version in ['0.4.0','0.4.1']:
            self.release['version']=version
            if version=='0.4.1':self.release.update(sourceCommit='a'*40,archiveSha256=self.f.old['pin']['toolkit']['archiveSha256'])
            r=self.observe();self.assertEqual(r['notices'],[])

    def test_security_attention_is_not_silently_cleared_by_ordinary_metadata(self):
        self.release.update(security=True,securitySource='synthetic:advisory/1');a=self.observe()
        self.next_attempt();self.release.update(security=False,securitySource=None)
        self.assertTrue(next(iter(self.observe(a['state'])['state']['assessments'].values()))['assessment']['securityRelevant'])

    def test_unrelated_deferral_does_not_repeat_notice(self):
        a=self.observe();self.next_attempt();self.request['policy']['deferrals'].append({'from':'0.4.1','to':'0.4.2','reason':'Unrelated'})
        self.assertEqual(self.observe(a['state'])['notices'],[])

    def test_new_json_families_and_operations_guide_are_declared(self):
        from tools.build_site import DOCUMENTS
        root=Path(__file__).resolve().parents[1]
        rows=json.loads((root/'standards/inspector-inventory.json').read_text())['records']
        self.assertTrue({'M-WATCH-REQUEST','M-WATCH-STATE','M-WATCH-RESULT'}<={r['id'] for r in rows})
        self.assertIn('OPERATIONS',[name for name,title in DOCUMENTS])

    def test_existing_empty_state_refuses_without_resetting_history(self):
        request=self.root/'watch.json';request.write_text(json.dumps(self.request));directory=self.root/'state'
        watch_files(request,directory,self.now,write=True)
        file=directory/'state.json';file.write_bytes(b'')
        with self.assertRaises(RecordError):watch_files(request,directory,self.now,write=True)
        self.assertEqual(file.read_bytes(),b'')

    def test_missing_identity_stays_unknown_and_restoring_anchor_recovers(self):
        a=self.observe();self.next_attempt();self.release['archiveSha256']=None
        b=self.observe(a['state']);entry=b['state']['assessments']['0.5.0']
        self.assertEqual(entry['status'],'blocked-unknown');self.assertFalse(entry['identityConflict'])
        self.assertEqual(entry['originalIdentity']['archiveSha256'],'c'*64)
        self.next_attempt('2026-11-07T12:00:00Z');self.release['archiveSha256']='c'*64
        c=self.observe(b['state']);self.assertEqual(c['state']['assessments']['0.5.0']['status'],'attention-required')
