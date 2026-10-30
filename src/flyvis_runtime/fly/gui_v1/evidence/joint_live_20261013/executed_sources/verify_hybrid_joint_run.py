"""Read-only joint PC/PS evidence audit. Never imports CUDA or connects a board."""
import argparse,dataclasses,json
from pathlib import Path
import numpy as np
from hybrid_v2 import V2Contract
from hybrid_a3 import module
from hybrid_joint_run import SavedReference,REFERENCE
from live_protocol import load,sha,require,host_path,write,Registry,HERE


def audit(run,board):
    run=host_path(run).resolve();board=host_path(board).resolve();c=V2Contract();w=c.wire
    scope=load(run/'scope.json');result=load(run/'result.json');pc=run/'pc'
    require(result['status']=='PC_THREE_COMMITS_PASS_PENDING_PS_AUDIT' and result['completed']==3,'PC_NOT_COMPLETED')
    require(result['producer_calls']==3 and result['native_H_production_updates']==0,'GPU_PRODUCTION_COUNT')
    require(load(run/'exit.json')['GPU_inflight_waited'] and load(run/'exit.json')['lease_closed'],'GPU_NOT_RELEASED')
    for name,digest in load(run/'manifest.json')['files'].items():
        p=(run/name).resolve();require(p.is_relative_to(run) and sha(p)==digest,'PC_FILE_CHANGED '+name)
    for name,digest in scope['source_sha256'].items():require(sha(HERE/name)==digest,'EXECUTED_SOURCE_CHANGED '+name)
    require(scope['model_steps']==[200,201,202] and scope['max_requests']==scope['max_commits']==3,'SHORT_SCOPE')
    prepared=load(board/'PREPARED.json');require(prepared['server_session']==scope['expected_server_session']
        and prepared['boot_id']==scope['expected_boot_id'] and prepared['new_loads']==prepared['new_resets']==0,'PS_PREPARED_IDENTITY')
    events=[json.loads(line) for line in (board/'events.jsonl').read_text().splitlines()]
    require(not any(e['event'] in ('LOAD_ATTEMPT_CONSUMED','LOAD_RETURNED','BUFFERS_ALLOCATED') for e in events),'UNEXPECTED_LOAD')
    require(not any(e['event']=='MMIO_WRITE_INTENT' and e['bank']=='dma' and e['offset'] in (0,0x30) for e in events),'UNEXPECTED_DMA_CONTROL')
    require(sum(e['event']=='DMA_LAUNCH_RETURNED' for e in events)==3 and sum(e['event']=='ACK_SENT' for e in events)==3,'PS_OPERATION_COUNT')
    require(any(e['event']=='THREE_RELEASES_COMPLETE' and e['requests']==e['commits']==3 for e in events),'PS_NOT_FINISHED')
    require(not any(e['event']=='FAILED_OR_UNKNOWN' for e in events),'PS_FAILED')
    firmware=load(pc/'firmware_session.json')
    require(firmware['boot_id']==prepared['boot_id'] and firmware['server_session']==prepared['server_session']
        and firmware['bit_sha256']==w.BIT_SHA and firmware['hwh_sha256']==w.HWH_SHA,'PC_PS_FIRMWARE')
    hmod=module('h_step',c.paths['h_step']);previous=np.load(pc/'initial_full.npy',allow_pickle=False)
    np.testing.assert_array_equal(previous,c.initial()[0]);frames=Registry().input('ON60')[0,200:203,0]
    journal=[json.loads(line) for line in (pc/'transactions.jsonl').read_text().splitlines()]
    require([e['event'] for e in journal]==['COMMIT_INTENT','COMMIT_ACK']*3,'DURABLE_COMMIT_JOURNAL')
    previous_words=(pc/'initial_H.bin').read_bytes();parent=bytes(32);previous_txn=bytes(16);rows=[];reference=SavedReference()
    for i,k in enumerate(range(200,203)):
        wire=(pc/f'request_{k}.bin').read_bytes();h=w.Header.unpack(wire[:256]);payload=wire[256:]
        require((board/f'request_{i}.bin').read_bytes()==wire,'PS_CURRENT_REQUEST')
        old=np.load(pc/f'old_full_{k}.npy',allow_pickle=False);np.testing.assert_array_equal(old,previous)
        require(h.step==k and h.old_sha.hex()==hmod.array_hash(old) and h.parent_commit==parent and h.previous_txn==previous_txn,'FULL_OLD_COMMIT_CHAIN')
        require(h.asid.hex()==firmware['asid'] and payload[:w.WORD_BYTES]==previous_words and w.digest(payload)==h.payload_sha,'OLD_PL_WORDS_INPUT_SHA')
        frame=np.load(pc/f'input_721_{k}.npy',allow_pickle=False);np.testing.assert_array_equal(frame,frames[i])
        chemical=np.load(pc/f'chemical_{k}.npy',allow_pickle=False)
        require(payload[w.WORD_BYTES:2*w.WORD_BYTES]==w.encode_activity(chemical),'CURRENT_CHEMICAL_WIRE')
        require(payload[2*w.WORD_BYTES:]==w.encode_activity(reference.candidates[i]['x_full'][c.h]),'CURRENT_X_H_WIRE')
        candidate=(pc/f'candidate_{k}.bin').read_bytes();require(candidate==(board/f'candidate_{i}.bin').read_bytes(),'PS_CURRENT_CANDIDATE')
        c.validate_H(payload,candidate)
        receipt=w.Header.unpack((pc/f'RESULT_{k}.bin').read_bytes())
        require(receipt.identity()==h.identity() and receipt.op==w.RESULT and receipt.status==0
            and receipt.payload_sha==w.digest(candidate) and receipt.transfer_cycles>=receipt.compute_cycles,'RESULT_IDENTITY')
        commit=w.Header.unpack((pc/f'COMMIT_{k}.bin').read_bytes());ack=w.Header.unpack((pc/f'ACK_{k}.bin').read_bytes())
        require(ack==dataclasses.replace(commit,op=w.ACK) and dataclasses.replace(commit,parent_commit=h.parent_commit).identity()==h.identity(),'ACK_COMMIT_MATCH')
        require(journal[i*2]['decision']==journal[i*2+1]['decision']==commit.parent_commit.hex()
            and journal[i*2+1]['ack_sha256']==w.digest(ack.pack()).hex(),'JOURNAL_ACK')
        release=[e for e in events if e['event']=='RELEASE_CONFIRMED' and e['step']==k];sent=[e for e in events if e['event']=='ACK_SENT' and e['step']==k]
        require(len(release)==len(sent)==1 and release[0]['state']==release[0]['error']==0
            and release[0]['txn']==sent[0]['txn']==h.txn.hex() and release[0]['commit_sha']==commit.parent_commit.hex()
            and release[0]['monotonic_ns']<sent[0]['monotonic_ns'],'PS_RELEASE_COMMIT')
        full=np.load(pc/f'committed_full_{k}.npy',allow_pickle=False);r=np.load(pc/f'R_candidate_{k}.npy',allow_pickle=False)
        np.testing.assert_array_equal(full[c.h],c.decode(candidate));np.testing.assert_array_equal(full[c.r],r)
        np.testing.assert_array_equal(full,np.load(pc/f'proposed_full_{k}.npy',allow_pickle=False))
        np.testing.assert_array_equal(c.spatial.extract(full),np.load(pc/f'spatial_{k}.npy',allow_pickle=False))
        row=load(pc/f'committed_step_{k}.json');require(row['run_id']==scope['run_id'] and row['state_token']==k+1
            and row['full_after_sha']==hmod.array_hash(full) and row['unified_commit_sha']==commit.parent_commit.hex()
            and row['input_sha']==hmod.array_hash(frame),'PUBLISHED_IDENTITY')
        flow=np.load(pc/f'flow_{k}.npy',allow_pickle=False);require(flow.shape==(2,721) and np.isfinite(flow).all(),'FLOW')
        require(np.allclose(flow,reference.flows[i],atol=1e-5,rtol=1e-5),'FLOW_NUMERIC')
        timing=load(board/f'timing_{i}.json')
        require(timing['core_cycles']==receipt.compute_cycles==57681 and timing['adapter_elapsed_cycles']==receipt.transfer_cycles,'PS_CYCLES')
        rows.append(dict(model_step=k,old_full_sha=h.old_sha.hex(),new_full_sha=hmod.array_hash(full),
            candidate_sha=w.digest(candidate).hex(),commit_sha=commit.parent_commit.hex(),PL_integer_error=0,
            flow_vs_mixed_reference_max_abs=float(np.max(np.abs(flow-reference.flows[i]))),
            PC_STEP_roundtrip_ns=row['PC_STEP_roundtrip_ns'],PC_COMMIT_roundtrip_ns=row['PC_COMMIT_roundtrip_ns'],
            core_cycles=receipt.compute_cycles,adapter_cycles=receipt.transfer_cycles,PS_timing=timing))
        previous=full;previous_words=candidate;parent=commit.parent_commit;previous_txn=h.txn
    return dict(status='PASS_ACTUAL_THREE_STEP_GPU_FPGA_CLOSED_LOOP',run_id=scope['run_id'],model_steps=[200,201,202],
        warm_start='Accepted Full output199; not a PL history for the prefix',PL_outputs_checked=17304,
        PL_feedback_words_checked=11536,R_nodes_per_step=39901,native_H_GPU_updates=0,official_flow_frames=3,
        PL_proven_global_ids=c.h.tolist(),mapping_sha256=c.mapping_sha,model=scope['model'],
        board_connected_now='SESSION_COMPLETED_NOT_LIVE',display_mode='OFFLINE_REPLAY_OF_ACTUAL_JOINT_RESULTS',
        BIT_SHA256=w.BIT_SHA,HWH_SHA256=w.HWH_SHA,boot_id=prepared['boot_id'],server_session=prepared['server_session'],
        input_sha256=scope['input_sha256'],rows=rows,new_loads=0,new_resets=0,REALTIME_STREAM_PASS='NOT_CLAIMED',
        pc_manifest_sha256=sha(run/'manifest.json'),board_files={str(p.relative_to(board)):sha(p) for p in board.rglob('*') if p.is_file()})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--run',required=True);ap.add_argument('--board',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    result=audit(a.run,a.board);write(host_path(a.output),result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('PL_proven_global_ids','board_files','rows')}))
