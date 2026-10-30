"""Explicit historical A3R1 board admission; never a live connection claim."""
import json,zipfile
from hybrid_a3 import inspect_local_board_replay
from live_protocol import HERE,load,host_path,require,sha


def board_acceptance(c):
    registry=load(HERE/'board_actual_registry.json')
    require(registry['schema']=='flyvis-accepted-board-replay/v1','BOARD_REGISTRY')
    root=host_path(registry['root']);pins=registry['files']
    for name,digest in pins.items():
        p=(root/name).resolve();require(p.is_relative_to(root.resolve()) and sha(p)==digest,'BOARD_EVIDENCE_CHANGED '+name)
    archive=root/registry['archive']
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if name.endswith('/'):continue
            p=(root/name).resolve();require(p.is_relative_to(root.resolve()) and p.read_bytes()==z.read(name),'BOARD_ARCHIVE_CONTENT')
    replay={name[len('pc_replay/'):]:digest for name,digest in pins.items() if name.startswith('pc_replay/')}
    check=inspect_local_board_replay(c,root/'pc_replay',replay)
    board=root/registry['board_events'];events=[json.loads(x) for x in (board/'events.jsonl').read_text().splitlines()]
    require(sum(e['event']=='LOAD_RETURNED' for e in events)==1 and sum(e['event']=='DMA_LAUNCH_RETURNED' for e in events)==3,'BOARD_OPERATION_COUNTS')
    for i,row in enumerate(check['historical_timing_rows']):
        step=row['step'];release=[e for e in events if e['event']=='RELEASE_CONFIRMED' and e['step']==step]
        ack=[e for e in events if e['event']=='ACK_SENT' and e['step']==step]
        require(len(release)==len(ack)==1 and release[0]['state']==release[0]['error']==0
            and release[0]['monotonic_ns']<ack[0]['monotonic_ns'],'RELEASE_BEFORE_ACK')
        require((board/f'request_{i}.bin').read_bytes()[256:]==(root/f'pc_replay/request_{i}.bin').read_bytes()
            and (board/f'candidate_{i}.bin').read_bytes()==(root/f'pc_replay/candidate_{i}.bin').read_bytes(),'PC_PS_BYTES_DIFFER')
    report=load(root/'pc_replay/BOARD_RESULT.json')
    return dict(status='PASS_INDEPENDENT_SAVED_BOARD_REPLAY',requests=3,values=17304,old_words_recurred=11536,
        archive_sha256=sha(archive),registry_sha256=sha(HERE/'board_actual_registry.json'),
        bit_sha256=c.wire.BIT_SHA,hwh_sha256=c.wire.HWH_SHA,
        old_boot_id=report['firmware_session']['boot_id'],old_server_session=report['firmware_session']['server_session'],
        evidence_level='ACTUAL_BOARD_REPLAY_NOT_GPU_JOINT',current_connection='NOT_CONNECTED',
        GPU_closed_loop='NOT_RUN',PL_proven_global_ids=[],timing_rows=report['rows'])
