"""Independently verify actual DOM observations and producer's software playback log."""
from datetime import datetime, timezone
import json
import re

from data_store import DataStore, ROOT, read_json, sha256
from phase3_adapter import Phase3Adapter


def main():
    root=ROOT/'gui_v1/evidence/phase4_unified_20261011'
    obs=read_json(root/'browser_observations.json');store=DataStore();p3=Phase3Adapter(store)
    pkg=next(iter(p3.packages.values()));f=pkg.frozen
    frozen=obs['frozen'];assert frozen['state'].startswith('INPUT_FROZEN')
    assert frozen['identity']['原comparison_id']==f.comparison_id
    assert json.loads(frozen['identity']['输入／初态／模型SHA'])==f.fingerprint
    assert json.loads(frozen['identity']['新采集／新推理'])=={'new_capture':False,'new_inference':False}
    assert 'job_id：NOT_AVAILABLE' in obs['missingBackend']['task'] and 'run_id：NOT_AVAILABLE' in obs['missingBackend']['task']
    assert obs['missingBackend']['state'].startswith('WAITING_COMPUTE') and 'not queued' in obs['missingBackend']['notice']
    count=0
    for row in [obs['replay'],obs['finalT4T5']]:
        k=int(re.search(r'step (\d+)/799',row['time'])[1])
        assert f'输入 {f.time[k]:.3f} s' in row['time'] and f'Euler后 {f.activity_time[k]:.3f} s' in row['time']
        assert f'原始源帧 {f.video.source_indices[k]} ·' in row['caption']
        for cell,value in re.findall(r'([A-Za-z]+[0-9]*[a-z]?) (-?\d+\.\d+)',row['readouts']):
            assert cell in f.cells
            actual=pkg.arrays['Python_Replacement'][k,f.central_ids[f.cells.index(cell)]]
            assert abs(float(value)-float(actual))<=.000501;count+=1
        assert 'COMMITTED_RECORDED · token '+str(k+1) in row['stages']
        assert 'NOT_APPLICABLE' in row['stages'] and 'NOT_RECORDED' in row['stages']
    assert count==11
    assert obs['replay']['identity']['run_id']==pkg.descriptor['modes']['Python_Replacement']['run_id']
    presentation=obs['presentation'];assert presentation['state'].startswith('PREVIEW_ONLY')
    assert not presentation['freezeEnabled'] and not presentation['replayEnabled'] and not presentation['workbenchVisible']
    assert presentation['clearedRun']['run_id']==presentation['clearedRun']['comparison_id']=='NOT_AVAILABLE'
    assert presentation['identity']['输入引用（非run）']=='NOT_AVAILABLE' and presentation['identity']['预览播放状态（非采集）']=='complete'
    pid=presentation['identity']['最近软件预览（未绑定输入）'];sid=pid.removeprefix('phone_')
    folder=ROOT/'gui_v1/runtime/unified_flow/presentations'/sid
    original=read_json(folder/'presentation.json');events=[json.loads(s) for s in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines()]
    assert original['presentation_id']==pid and original['validation_only'] is True
    assert original['state']=='complete' and original['camera_capture'] is original['neural_inference'] is original['physical_phone_verified'] is False
    assert original['comparison_id'] is None and original['settings_sha256']==presentation['identity']['预览参数SHA（非输入SHA）']
    assert original['settings']['direction_deg']==90 and original['settings']['polarity']=='ON'
    kinds=[r['client_event']['kind'] for r in events];assert kinds.count('start')==1 and 'frame' in kinds and 'complete' in kinds
    camera=obs['camera'];assert camera['dataset']=='camera1' and camera['execution']=='录制结果回放'
    assert camera['state'].startswith('PREVIEW_ONLY') and not camera['freezeEnabled'] and not camera['workbenchVisible']
    k=int(camera['frame']);c=store.datasets['camera1'].info()['camera'];source=c['input_source_indices'][k]
    assert camera['sourceClock'].startswith(f'源帧 {source} / {c["source_time_s"][source]:.6f} s')
    assert camera['inputClock']==f'{k*.005:.3f} s' and camera['activityClock']==f'{k*.005+.005:.3f} s'
    d=obs['legacyDirection'];assert d['condition']=='180° / OFF / v=19' and d['playEnabled']
    metric=store.datasets['edge24'].directions('T4c',0)['official_metric'];assert abs(float(d['dsi'])-metric['official_dsi'])<=.000051
    layout=obs['finalLayout'];assert layout['page']<=layout['viewport'] and layout['flowWidth']>.9*layout['mainWidth']
    report={'schema':'flyvis-unified-browser-acceptance-v1','status':'PASS_SOFTWARE_BROWSER_ONLY',
        'utc':datetime.now(timezone.utc).isoformat(),'actual_activity_readouts_checked':count,
        'software_presentation_id':pid,'presentation_sha256':sha256(folder/'presentation.json'),
        'presentation_log_sha256':sha256(folder/'events.jsonl'),'actual_software_frame_callbacks':kinds.count('frame'),
        'presentation_complete_does_not_freeze_or_infer':True,'input_change_clears_old_identity':True,
        'camera_sample_three_clocks':True,'legacy_direction_OFF_and_DSI':True,'new_camera_capture':False,
        'new_inference':False,'board_execution':False,'real_new_phone_input_positive':'NOT_RUN',
        'real_job_positive':'NOT_RUN','observations_sha256':sha256(root/'browser_observations.json')}
    (root/'browser_acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__':main()
