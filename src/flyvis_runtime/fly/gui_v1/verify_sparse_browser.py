"""Validate actual CUA browser observations against sealed arrays and CSV."""
import csv
from datetime import datetime,timezone
import json
from pathlib import Path
import re

import numpy as np
from data_store import ROOT,read_json,sha256
from scientific_sparse import COUNTS,CONDITIONS,METRICS


def main():
    folder=ROOT/'gui_v1/evidence/scientific_sparse_20261012';observed=read_json(folder/'browser_observations.json')
    source=Path(read_json(ROOT/'gui_v1/scientific_sparse.json')['directory'])
    pilot=Path(read_json(ROOT/'gui_v1/scientific_pilot.json')['directory'])
    with (source/'sparsity_curve.csv').open(encoding='utf-8',newline='') as stream:
        rows={(r['condition'],int(r['n_retained'])):r for r in csv.DictReader(stream)}
    checked=[]
    for observation in observed['observations']+[observed['playing'],observed['paused']]:
        c,count,k=observation['condition'],observation['count'],observation['step'];assert c in CONDITIONS and count in COUNTS and not observation['hidden']
        array=np.load(source/f'artifacts/gpu_r1/{c}/KEEP_{count}/flow.npy',mmap_mode='r')[0]
        zero=np.load(source/f'artifacts/gpu_r1/{c}/KEEP_0/flow.npy',mmap_mode='r')[0]
        full=np.load(pilot/f'artifacts/pilot_gpu_r1/{c}/Full/flow.npy',mmap_mode='r')[0]
        vectors=[float(v) for v in re.findall(r'[xy]=(-?\d+\.\d+)',observation['vector'])]
        expected=[a[k,ch,360] for a in (full,zero,array) for ch in (0,1)]
        assert len(vectors)==6 and np.allclose(vectors,expected,rtol=0,atol=5.01e-7)
        times=[float(v) for v in re.findall(r'(-?\d+\.\d+) s',observation['time'])]
        assert np.allclose(times,[k*.005-1,(k+1)*.005-1],rtol=0,atol=1e-12) and 'OFFLINE_REPLAY' in observation['time']
        assert ('钳制窗口前' if k<200 else 'k200 后钳制') in observation['time']
        fields=[float(v) for v in re.findall(r'(?:E |场角 / ° |M |Q )(-?\d+\.\d+)',observation['metrics'])]
        expected=[float(rows[c,n][key]) for n in (5768,0,count) for key in METRICS]
        assert len(fields)==12 and np.allclose(fields,expected,rtol=0,atol=5.01e-7)
        chart=[float(v) for v in re.findall(r'(?:E |场角 |M |Q )(-?\d+\.\d+)',observation['chart'])]
        assert len(chart)==8 and np.allclose(chart,[float(rows[cond,count][key]) for cond in CONDITIONS for key in METRICS],rtol=0,atol=5.01e-7)
        keep=np.load(source/f'keep_{count}.npy');assert f'实际保留 {count} / 5768' in observation['set'] and f'未保留 {5768-count}' in observation['set']
        actual_types=[int(v) for v in re.findall(r'T[45][abcd] (\d+)',observation['types'])];assert len(actual_types)==8 and sum(actual_types)==count and len(set(actual_types))==1
        assert sha256(source/f'keep_{count}.npy') in observation['hash'] and sha256(source/f'inactive_{count}.npy') in observation['hash']
        for node in keep[:12]:assert str(node) in observation['ids']
        if count==0:assert '[]' in observation['ids']
        assert c in observation['input'] and 'KEEP_'+str(count) in observation['selected']
        checked.append({'condition':c,'count':count,'step':k,'original_fields_metrics_sets_times_match':True})
    assert {(r['condition'],r['count']) for r in observed['observations']}=={(c,n) for c in CONDITIONS for n in COUNTS}
    assert {199,200,484}.issubset({r['step'] for r in checked})
    assert observed['playing']['play']=='Ⅱ 暂停离线回放' and observed['paused']['play']=='▶ 播放离线回放' and observed['paused']['step']>observed['playing']['step']
    assert observed['chartClick']['count']==2648
    page=observed['page'];assert page['status'].startswith('VERIFIED') and 'SOFTWARE_SPARSE_RETAIN / OFFLINE_REPLAY' in page['status']
    assert len(page['oldDatasets'])==7 and page['oldDsi']=='0.6274' and 'unavailable' in page['oldP0']
    assert 'SOFTWARE_PILOT' in page['pilot'] and 'COMPLETE' in page['runner'] and 'NOT_CONNECTED' in page['runner']
    assert page['oldSparsePlaceholderHidden'] and len(page['canvases'])==8 and all(v['width']>100 and v['height']>100 for v in page['canvases'])
    assert page['panelWidth']>.9*page['mainWidth'] and not observed['logs']
    assert 'bb431767-0816-4826-8a5b-2a469dd86d65' in page['identity'] and '2041849d-b1f8-46ad-a059-49b598c19ab2' in page['identity'] and 'NOT_CONNECTED' in page['identity']
    report={'status':'PASS_LIMITED_REAL_BROWSER_SPARSE','utc':datetime.now(timezone.utc).isoformat(),
        'observations_verified':checked,'vector_readouts':len(checked)*6,'primary_metric_readouts':len(checked)*12,
        'two_condition_chart_readouts':len(checked)*8,'all14_cases_selected':True,'step199_200_484_sync':True,
        'actual_node_set_identity_display':True,'chart_click_selects_actual_scale':True,'offline_play_pause_observed':True,
        'old55_seven_choices_DSI_P0_pilot_runner_preserved':True,'four_charts_four_fields_visible':True,'console_errors':0,
        'evidence_level':'GUI_SOFTWARE_SPARSE_RETAIN_OFFLINE_REPLAY_ONLY','new_neural_computation':False,'PL_execution':False}
    (folder/'browser_acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','vector_readouts','primary_metric_readouts','all14_cases_selected')}))


if __name__=='__main__':main()
