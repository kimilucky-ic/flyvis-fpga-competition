"""Check saved actual DOM observations and actual browser CSV against accepted P0."""
import argparse
import csv
from datetime import datetime,timezone
import json
from pathlib import Path
import re
import numpy as np
from data_store import DataStore,ROOT,TARGETS,sha256,read_json
from phase3_adapter import Phase3Adapter


def main():
    p=argparse.ArgumentParser();p.add_argument('--observations',default=str(ROOT/'gui_v1/evidence/phase4/browser_observations.json'));p.add_argument('--csv',required=True);args=p.parse_args()
    obs=read_json(args.observations);store=DataStore();adapter=Phase3Adapter(store);pkg=next(iter(adapter.packages.values()));f=pkg.frozen
    values=0
    for row in obs['observations']:
        if not row['viewVisible']:
            assert 'NOT_AVAILABLE' in row['current'] and row['identity']['run_id']=='NOT_AVAILABLE' and row['identity']['实际 backend']=='NOT_AVAILABLE' and not row['stages'];continue
        mode='Full_GPU' if row['identity']['当前模式']=='Full GPU' else 'Python_Replacement';run=pkg.descriptor['modes'][mode]
        k=int(re.search(r'step (\d+)/799',row['time'])[1])
        assert row['identity']['run_id']==run['run_id'] and row['identity']['comparison_id']==f.comparison_id and row['identity']['本次活动来源 SHA']==run['source_activity_sha256']
        assert row['identity']['display_kind']=='offline replay' and row['identity']['当前真板连接']=='NOT_AVAILABLE' and row['identity']['板卡／bit／hwh']=='NOT_AVAILABLE'
        assert f'输入 {f.time[k]:.3f} s' in row['time'] and f'Euler后 {f.activity_time[k]:.3f} s' in row['time']
        assert f'原始源帧 {f.video.source_indices[k]} ·' in row['caption']
        for cell,value in re.findall(r'(T[45][a-d]) (-?\d+\.\d+)',row['readouts']):
            actual=pkg.arrays[mode][k,f.central_ids[f.cells.index(cell)]];assert abs(float(value)-float(actual))<=.000501;values+=1
        assert '返回候选NOT_RECORDED' in row['stages'] and 'PL计算／历史记录NOT_APPLICABLE' in row['stages'] and '实际校验PASS_SOURCE_CHAIN' in row['stages']
        assert ('统一 COMMITREFERENCE_RECORDED' if mode=='Full_GPU' else f'统一 COMMITCOMMITTED_RECORDED · token {k+1}') in row['stages']
        assert row['pageWidth']<=row['viewportWidth'] and not row['errors'] and all(c['width']>0 and c['height']>0 for c in row['canvasSizes'])
    assert values>=80 and not obs['normal_console_errors']
    assert obs['unavailable']['submit'].startswith('NOT_AVAILABLE · 未创建任务') and obs['unavailable']['legacy']=={'dataset':'edge24','dsi':'0.6274','playEnabled':True}
    assert not obs['fault']['viewVisible'] and 'NOT_AVAILABLE' in obs['fault']['current'] and obs['fault']['legacyPlayable'] and obs['fault']['legacyDSI']=='0.6274'
    assert obs['legacy_smoke']['datasets']==['edge24','flash','bar','minimal','camera1','bar10','controlled6'] and len(obs['legacy_smoke']['conditions'])==7
    for r in obs['legacy_smoke']['conditions']:assert r['playEnabled'] and r['curveCount']==8
    with Path(args.csv).open(encoding='utf-8',newline='') as stream:rows=list(csv.DictReader(stream))
    run=pkg.descriptor['modes']['Python_Replacement'];assert len(rows)==800
    for k,row in enumerate(rows):
        assert row['comparison_id']==f.comparison_id and row['run_id']==run['run_id'] and row['mode']=='Python_Replacement' and row['display_kind']=='offline_replay' and row['source_activity_sha256']==run['source_activity_sha256'] and int(row['step_id'])==k
        assert float(row['input_time_s'])==f.time[k] and float(row['activity_time_s'])==f.activity_time[k]
        exported=np.asarray([float(row[c]) for c in f.cells],dtype='<f4')
        assert np.array_equal(exported,pkg.arrays['Python_Replacement'][k,f.central_ids])
    result={'schema':'flyvis-phase4-browser-acceptance-v1','status':'PASS','utc':datetime.now(timezone.utc).isoformat(),'actual_DOM_readouts_verified':values,'CSV_rows':800,'CSV_values_bitwise_verified':52000,'CSV_sha256':sha256(args.csv),'all_four_modes_and_missing_results':True,'current_connection_not_inferred_from_history':True,'legacy_seven_dataset_smoke':True,'workbench_source_failure_preserves_legacy':True,'normal_console_errors':[],'offline_replay_only':True,'board_executed':False,'new_inference_executed':False,'real_board_browser_positive':'NOT_RUN: producer result/backend absent'}
    path=ROOT/'gui_v1/evidence/phase4/browser_acceptance.json';path.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'status':'PASS','readouts':values,'csv_values':52000,'output':str(path)}))


if __name__=='__main__':main()
