"""Fail-closed human-window/technical-review gate. No neural or CUDA imports."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,shutil

HERE=Path(__file__).resolve().parent
class LaunchBlocked(RuntimeError):pass
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def parse_time(s):
    if not isinstance(s,str):raise LaunchBlocked('missing explicit start/end')
    try:d=datetime.fromisoformat(s)
    except ValueError as e:raise LaunchBlocked('invalid start/end') from e
    if d.tzinfo is None:raise LaunchBlocked('timezone required')
    return d.astimezone(timezone.utc)
def validate_window(campaign,technical,coord,window,now=None):
    now=now or datetime.now(timezone.utc)
    cid=campaign['campaign_id']
    if technical.get('decision')!='APPROVE_UNCHANGED_v1':raise LaunchBlocked('technical review not ratified')
    for document in [technical,coord,window]:
        if document.get('campaign_id')!=cid:raise LaunchBlocked('campaign identity mismatch')
    if technical.get('proposal_sha256')!=campaign['proposal_sha256']:raise LaunchBlocked('technical review binds another proposal')
    if not technical.get('authoritative_record'):raise LaunchBlocked('no authoritative technical review record')
    if coord.get('conflict_free') is not True or coord.get('owner')!='A_GPU':raise LaunchBlocked('A GPU coordination not confirmed')
    if coord.get('GPU_uuid')!=campaign['GPU_uuid']:raise LaunchBlocked('GPU differs from coordinated device')
    if window.get('human_run_authorized') is not True:raise LaunchBlocked('no human run authorization')
    if not window.get('authorization_source') or not window.get('human_confirmation_text'):raise LaunchBlocked('human authorization evidence absent')
    if window.get('GPU_uuid')!=campaign['GPU_uuid']:raise LaunchBlocked('authorized GPU mismatch')
    if window.get('candidate_ids')!=campaign['candidate_ids']:raise LaunchBlocked('approved candidate order differs')
    if window.get('proposal_sha256')!=campaign['proposal_sha256']:raise LaunchBlocked('authorized metrics/thresholds differ')
    start,end=parse_time(window.get('start')),parse_time(window.get('end'))
    if not 0<(end-start).total_seconds()<=90*60:raise LaunchBlocked('window must be explicit and at most90 minutes')
    if not start<=now<end:raise LaunchBlocked('window is future or expired')
    # A's own confirmed availability must cover the entire human window.
    if parse_time(coord.get('available_start'))>start or parse_time(coord.get('available_end'))<end:
        raise LaunchBlocked('A availability does not cover requested window')
    if parse_time(coord.get('valid_until'))<now:raise LaunchBlocked('A confirmation expired')
    return end
def verify_frozen_files():
    p=HERE/'FROZEN_CAMPAIGN_IDENTITY.json'
    if not p.exists():raise LaunchBlocked('campaign identity not frozen')
    identity=load(p)
    core=identity['canonical_core']
    actual=hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    if identity['campaign_id']!=actual:raise LaunchBlocked('canonical campaign hash mismatch')
    for e in identity['files']:
        target=HERE/e['path']
        if not target.exists() or target.stat().st_size!=e['bytes'] or sha(target)!=e['sha256']:
            raise LaunchBlocked('frozen input/code changed: '+e['path'])
    return identity
def require_launch():
    identity=verify_frozen_files()
    # Mutable authority records are intentionally outside immutable experiment identity.
    names=['TECHNICAL_RATIFICATION.json','GPU_COORDINATION_CONFIRMED.json','RUN_WINDOW_AUTHORIZATION.json']
    if not all((HERE/n).exists() for n in names):raise LaunchBlocked('technical/coordination/human-window record absent')
    t,c,w=[load(HERE/n) for n in names]
    end=validate_window(identity,t,c,w)
    art=HERE/'artifacts'
    written=sum(p.stat().st_size for p in art.rglob('*') if p.is_file()) if art.exists() else 0
    remaining=max(0,28*1024**3-written)
    if shutil.disk_usage(HERE).free<remaining+8*1024**3:raise LaunchBlocked('disk below remaining28GiB budget +8GiB headroom')
    return dict(end=end,identity=identity,authority_sha256={n:sha(HERE/n) for n in names})
def require_step_time(ticket):
    if datetime.now(timezone.utc)>=ticket['end']:raise LaunchBlocked('window ended; no next-state commit permitted')
