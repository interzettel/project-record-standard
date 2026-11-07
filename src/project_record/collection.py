"""Retains quiet sourced release attention without collecting or applying updates."""
from copy import deepcopy
from datetime import datetime,timedelta,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re

from .core import RecordError
from .pins import validate_pin,verify_installation,assess_update,_version,_match,_COMMIT,_DIGEST,_file
from .upgrades import _read
from .upgrade_apply import _root
from .reconcile import _atomic,_lock


def _json(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()


def _hash(value):return sha256(_json(value)).hexdigest()


def _clock(value):
    if not isinstance(value,str):raise RecordError('Explicit zoned ISO clock required')
    try:t=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as error:raise RecordError('Invalid observation clock') from error
    if t.tzinfo is None:raise RecordError('Observation clocks require timezone')
    return t.astimezone(timezone.utc)


def _iso(t):return t.isoformat().replace('+00:00','Z')


def _installation(request):
    pin=request['pin'];host=_root(request['host']);paths={'AGENTS.md','.project-record/agent-installation.json'}|set(pin['suite']['files'])
    paths|={'/'.join(x for x in [pin['toolkit']['prefix'],p] if x) for p in pin['toolkit']['files']}
    if pin['policy'] is not None:paths.add(pin['policy']['path'])
    try:
        for relative in paths:
            path=_file(host,relative)
            if path.exists():_read(path)
        return verify_installation(pin,host,request['provenance'],request['runtime'])
    except (OSError,RecordError):return {'bytes':'conflicted','provenance':'not-assessed','runtime':{},'adapters':{}}


def _validate(request):
    fields={'watchVersion','consumerId','host','pin','provenance','runtime','policy','collection'}
    if not isinstance(request,dict) or set(request)!=fields or type(request['watchVersion']) is not int or request['watchVersion']!=1:raise RecordError('Use exact watchVersion1 fields')
    if not isinstance(request['consumerId'],str) or not re.fullmatch('[a-zA-Z0-9][a-zA-Z0-9_.-]{0,127}',request['consumerId']):raise RecordError('Explicit consumer identity required')
    validate_pin(request['pin']);_root(request['host'])
    if not isinstance(request['runtime'],dict):raise RecordError('Observed runtime map required')
    for v in request['runtime'].values():_version(v)
    p=request['policy']
    if not isinstance(p,dict) or set(p)!={'intervalSeconds','freshnessSeconds','retrySeconds','maxRetries','deferrals'}:raise RecordError('Explicit host schedule/retry policy required')
    for k in ['intervalSeconds','freshnessSeconds','retrySeconds','maxRetries']:
        if type(p[k]) is not int or not (0<=p[k]<=31536000) or (k!='maxRetries' and p[k]==0):raise RecordError('Invalid bounded schedule policy')
    if p['maxRetries']>10 or not isinstance(p['deferrals'],list):raise RecordError('Retry/deferral bounds invalid')
    targets=set()
    for d in p['deferrals']:
        if not isinstance(d,dict) or set(d)!={'from','to','reason'} or not isinstance(d['reason'],str) or not d['reason'].strip():raise RecordError('Exact from/to reasoned deferral required')
        _version(d['from']);_version(d['to'])
        if (d['from'],d['to']) in targets:raise RecordError('Duplicate deferral')
        targets.add((d['from'],d['to']))
    c=request['collection']
    if not isinstance(c,dict) or set(c)!={'attemptedAt','status','source','coverage','releases','error'} or c['status'] not in {'success','partial','failed','unknown'} or not isinstance(c['source'],str) or not c['source'].strip():raise RecordError('Sourced collection envelope required')
    _clock(c['attemptedAt']);coverage=c['coverage']
    if not isinstance(coverage,dict) or set(coverage)!={'pagesRead','pagesExpected'}:raise RecordError('Explicit page coverage required')
    read,expected=coverage['pagesRead'],coverage['pagesExpected']
    if type(read) is not int or read<0 or (expected is not None and (type(expected) is not int or expected<1 or read>expected)):raise RecordError('Invalid page coverage')
    if not isinstance(c['releases'],list) or len(c['releases'])>1000 or (c['error'] is not None and not isinstance(c['error'],str)):raise RecordError('Bounded release list/error required')
    versions=set()
    for release in c['releases']:
        if not isinstance(release,dict) or set(release)!={'version','sourceCommit','archiveSha256','notesSha256','security','securitySource','source'}:raise RecordError('Explicit release evidence fields required')
        _version(release['version'])
        if release['version'] in versions:raise RecordError('Duplicate target version')
        versions.add(release['version'])
        for key,pattern in [('sourceCommit',_COMMIT),('archiveSha256',_DIGEST),('notesSha256',_DIGEST)]:
            if release[key] is not None and not _match(pattern,release[key]):raise RecordError('Immutable release evidence or null required')
        if type(release['security']) is not bool or not isinstance(release['source'],str) or not release['source'].strip():raise RecordError('Sourced release/security status required')
        if release['securitySource'] is not None and (not isinstance(release['securitySource'],str) or not release['securitySource'].strip()):raise RecordError('Invalid security source')
        if release['security'] and release['securitySource'] is None:raise RecordError('Security relevance requires attributed evidence')


def _validate_state(state,consumer):
    fields={'watchStateVersion','consumerId','lastAttempt','lastSuccess','nextDue','retryCount','assessments','stateSha256'}
    if not isinstance(state,dict) or set(state)!=fields or type(state['watchStateVersion']) is not int or state['watchStateVersion']!=1 or state['consumerId']!=consumer or state['stateSha256']!=_hash({k:v for k,v in state.items() if k!='stateSha256'}):raise RecordError('Private watcher state identity/digest conflict')
    if not isinstance(state['assessments'],dict) or len(state['assessments'])>1000 or type(state['retryCount']) is not int or state['retryCount']<0:raise RecordError('Corrupt watcher state bounds')
    if state['lastAttempt'] is not None:_clock(state['lastAttempt']['attemptedAt'])
    if state['lastSuccess'] is not None:_clock(state['lastSuccess']['attemptedAt'])
    if state['nextDue'] is not None:_clock(state['nextDue'])


def observe_releases(request,as_of,state=None):
    """Returns dated attention assessments from supplied observations and local pins.

    Source completeness/security attribution are caller claims, not authenticated
    collection or vulnerability verification. This is not a semantic migration.
    """
    _validate(request);now=_clock(as_of);attempt=_clock(request['collection']['attemptedAt'])
    if attempt>now:raise RecordError('Collection attempt cannot be in the future')
    previous=deepcopy(state)
    if state is None:
        state={'watchStateVersion':1,'consumerId':request['consumerId'],'lastAttempt':None,'lastSuccess':None,'nextDue':None,'retryCount':0,'assessments':{}}
    else:_validate_state(state,request['consumerId']);state=deepcopy(state)
    pin_result=_installation(request);pin_ok=pin_result['bytes']=='selected-bytes-match' and pin_result['provenance']=='matches-declared-evidence'
    c=request['collection'];p=request['policy'];complete=c['status']=='success' and c['coverage']['pagesExpected'] is not None and c['coverage']['pagesRead']==c['coverage']['pagesExpected'] and c['error'] is None
    request_hash=_hash(request);old_attempt=state['lastAttempt'];replay=False
    if old_attempt:
        old_time=_clock(old_attempt['attemptedAt'])
        if attempt<old_time:raise RecordError('Collection clock regressed')
        if attempt==old_time:
            if old_attempt['requestSha256']!=request_hash:raise RecordError('Same attempt identity changed; preserve original observation')
            replay=True
    late=state['nextDue'] is not None and attempt>_clock(state['nextDue'])
    notices=[]
    identity={k:request['pin']['toolkit'][k] for k in ['version','sourceCommit','archiveSha256']}
    if not replay:
        for release in c['releases']:
            version=release['version'];prior=state['assessments'].get(version)
            immutable={k:release[k] for k in ['sourceCommit','archiveSha256']}
            original=deepcopy(prior['originalIdentity']) if prior else deepcopy(immutable)
            moved=bool(prior and (prior['identityConflict'] or any(original[k] is not None and immutable[k] is not None and immutable[k]!=original[k] for k in original)))
            if version==identity['version'] and any(immutable[k] is not None and identity[k] is not None and immutable[k]!=identity[k] for k in immutable):moved=True
            original={k:original[k] if original[k] is not None else immutable[k] for k in original}
            deferral=next((d for d in p['deferrals'] if d['from']==identity['version'] and d['to']==version),None)
            fingerprint=_hash({'release':release,'installed':identity,'pinVerified':pin_ok,'complete':complete,'deferral':deferral})
            if prior and prior['fingerprint']==fingerprint:continue
            deferral=next((d for d in p['deferrals'] if d['from']==identity['version'] and d['to']==version),None)
            security_source=release['securitySource'] if release['security'] else prior.get('securityEvidence') if prior else None
            assessment=assess_update(identity['version'],version,security=security_source is not None,deferral=deferral)
            status='conflicted' if moved else 'blocked-unknown' if not (pin_ok and complete and release['sourceCommit'] and release['archiveSha256']) else 'attention-required'
            entry={'release':deepcopy(release),'installedIdentity':identity,'originalIdentity':original,'identityConflict':moved,'status':status,'assessment':assessment,'securityEvidence':security_source,'source':c['source'],'coverage':deepcopy(c['coverage']),'firstObservedAt':prior['firstObservedAt'] if prior else _iso(attempt),'assessedAt':_iso(attempt),'revision':prior['revision']+1 if prior else 1,'fingerprint':fingerprint,'semanticAssessment':'Use upgrade-project-records/#20 with reviewed archives and complete intervening deltas; no semantic compatibility certified'}
            relevant=assessment['change'] not in {'unchanged','downgrade'} or assessment['securityRelevant'] or moved
            if not relevant:entry['status']='no-attention'
            state['assessments'][version]=entry
            if relevant:notices.append({'consumerId':request['consumerId'],'targetVersion':version,'revision':entry['revision'],'status':status,'disposition':assessment['disposition']})
        if len(state['assessments'])>1000:raise RecordError('State retention bound reached; explicit archival policy required')
        state['lastAttempt']={'attemptedAt':_iso(attempt),'requestSha256':request_hash,'source':c['source'],'status':c['status'],'coverage':deepcopy(c['coverage']),'error':c['error'],'complete':complete,'pinVerified':pin_ok}
        if complete and pin_ok:
            state['lastSuccess']={'attemptedAt':_iso(attempt),'installedIdentity':identity,'releaseCount':len(c['releases']),'source':c['source']};state['retryCount']=0;state['nextDue']=_iso(attempt+timedelta(seconds=p['intervalSeconds']))
        else:
            state['retryCount']+=1;state['nextDue']=None if state['retryCount']>p['maxRetries'] else _iso(attempt+timedelta(seconds=p['retrySeconds']))
        state['stateSha256']=_hash({k:v for k,v in state.items() if k!='stateSha256'})
    success=state['lastSuccess'];last=state['lastAttempt']
    health='retry-exhausted' if state['retryCount']>p['maxRetries'] else 'degraded' if not(last['complete'] and last['pinVerified'] and pin_ok) else 'stale' if success is None or (now-_clock(success['attemptedAt'])).total_seconds()>p['freshnessSeconds'] else 'current'
    return {'watchResultVersion':1,'consumerId':request['consumerId'],'asOf':_iso(now),'state':state,'changed':state!=previous,'notices':notices,'health':health,'lateAttempt':late and not replay,'scheduleMissed':state['nextDue'] is not None and now>_clock(state['nextDue']),'lastSuccess':deepcopy(success),'nextDue':state['nextDue'],'pinVerification':pin_result,'written':False,'applicationAuthorized':False,'upgradeApplied':False,'limits':['Supplied collection coverage and security relevance are not authenticated','Attention assessment reuses version policy; full semantic comparison/application remain separate','No network, scheduler, notifications, GitHub or consumer writes; caller decides bounded transport']}


def watch_files(request_path:Path,state_directory:Path,as_of:str,*,write=False):
    """Previews or atomically replaces only an external private state.json."""
    request_path=_root(request_path);directory=_root(state_directory)
    try:request=json.loads(_read(request_path,1024*1024))
    except RecursionError as error:raise RecordError('Request nesting unsupported') from error
    _validate(request);host=_root(request['host'])
    if directory==host or host in directory.parents or directory in host.parents or directory==request_path or directory in request_path.parents:raise RecordError('State must be external to host and request')
    def run():
        file=directory/'state.json';before=None
        if directory.exists():
            if not directory.is_dir() or {p.name for p in directory.iterdir()}!={'state.json'}:raise RecordError('Unknown or incomplete watcher output directory')
            if os.name!='nt' and (directory.stat().st_mode&0o077 or file.stat().st_mode&0o077):raise RecordError('Watcher state must be owner-private')
            before=_read(file,8*1024*1024)
        try:state=json.loads(before) if before is not None else None
        except (ValueError,RecursionError) as error:raise RecordError('Corrupt watcher state; retain for recovery') from error
        result=observe_releases(request,as_of,state)
        if write and result['changed']:
            data=_json(result['state'])
            if len(data)>8*1024*1024:raise RecordError('State byte budget exceeded')
            directory.mkdir(mode=0o700,parents=True,exist_ok=True);_atomic(file,data);result['written']=True
        return result
    if not write:return run()
    # The lock is outside the owned directory and serializes cooperating writers.
    directory.parent.mkdir(parents=True,exist_ok=True)
    lock=Path(str(directory)+'.prs-lock')
    if lock.exists() and (lock.is_symlink() or not lock.is_file()):raise RecordError('Unsafe watcher lock')
    with _lock(directory):return run()
