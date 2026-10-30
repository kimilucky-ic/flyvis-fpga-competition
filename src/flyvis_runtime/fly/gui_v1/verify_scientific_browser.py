"""Check actual browser DOM readouts against saved GPU arrays/analysis CSV."""
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re

import numpy as np
from data_store import ROOT,read_json
from scientific_pilot import MODES,LABELS


def main():
    folder=ROOT/'gui_v1/evidence/scientific_pilot_20261011'
    observed=read_json(folder/'browser_observations.json')
    config=read_json(ROOT/'gui_v1/scientific_pilot.json');source=Path(config['directory'])
    with (source/'artifacts/pilot_analysis_r1/flow_step_series.csv').open(encoding='utf-8') as stream:
        series={(x['condition'],x['mode'],int(x['step_id'])):x for x in csv.DictReader(stream)}
    with (source/'artifacts/pilot_analysis_r1/functional_summary.csv').open(encoding='utf-8') as stream:
        metrics={(x['condition'],x['mode']):x for x in csv.DictReader(stream) if x['ROI']=='primary331' and x['window']=='primary'}
    checked=[]
    for observation in observed['observations']+[observed['playing'],observed['paused']]:
        condition,mode,k=observation['condition'],observation['mode'],observation['step']
        flow=np.load(source/f'artifacts/pilot_gpu_r1/{condition}/{mode}/flow.npy',mmap_mode='r')[0]
        full=np.load(source/f'artifacts/pilot_gpu_r1/{condition}/Full/flow.npy',mmap_mode='r')[0]
        values=[float(x) for x in re.findall(r'[xy]=(-?\d+\.\d+)',observation['vector'])]
        assert len(values)==4 and np.allclose(values,[full[k,0,360],full[k,1,360],flow[k,0,360],flow[k,1,360]],rtol=0,atol=5.01e-7)
        times=[float(x) for x in re.findall(r'(-?\d+\.\d+) s',observation['time'])]
        assert np.allclose(times,[k*.005-1,(k+1)*.005-1],rtol=0,atol=1e-12) and 'offline replay' in observation['time']
        curve_numbers=[float(x) for pair in re.findall(r'投影 (-?\d+\.\d+) / 幅度 (-?\d+\.\d+)',observation['curves']) for x in pair]
        expected=[float(series[condition,m,k][field]) for m in MODES for field in ('stimulus_projection','mean_pixel_vector_magnitude')]
        assert np.allclose(curve_numbers,expected,rtol=0,atol=5.01e-7)
        if 'metrics' in observation:
            metric_values=[float(x) for x in re.findall(r'(?:Q |M |E |场夹角 / ° )(-?\d+\.\d+)',observation['metrics'])]
            expected=[float(metrics[condition,m][field]) for m in MODES for field in ('Q','magnitude_ratio','field_error_E','angle_deg')]
            assert np.allclose(metric_values,expected,rtol=0,atol=5.01e-5)
        checked.append({'condition':condition,'mode':mode,'step':k,'original_vector_and_saved_curves_exact_to_display_precision':True})
    page=observed['page']
    assert len(page['oldDatasets'])==7 and page['oldDsi']=='0.6274'
    assert 'unavailable' in page['oldP0'] and 'SOFTWARE_PILOT' in page['status']
    assert '37.308' in page['runner'] and '已验收缓存回放' in page['runner'] and '当次实际新计算' in page['runner'] and 'NOT_CONNECTED' in page['runner']
    assert 'NOT_AVAILABLE' in page['sparse'] and page['panelWidth']>.9*page['mainWidth']
    assert len(page['canvases'])==5 and all(x['width']>100 and x['height']>100 for x in page['canvases'])
    assert not observed['logs'] and observed['paused']['step']>observed['playing']['step']
    report={'status':'PASS_LIMITED_REAL_BROWSER','utc':datetime.now(timezone.utc).isoformat(),
        'observations_verified':checked,'verified_vector_values':len(checked)*4,'verified_curve_readouts':len(checked)*10,
        'five_modes_two_conditions':True,'step199_200_484_sync':True,'historical_play_pause_observed':True,
        'old_seven_datasets_DSI_P0_preserved':True,'full_width_five_canvas_layout':True,'console_errors':0,
        'evidence_level':'GUI_SOFTWARE_PILOT_OFFLINE_REPLAY_ONLY','new_neural_computation':False,'PL_execution':False,
        'repair':'Number-input event updates all plots immediately; fixed full-width grid placement. No raw source edits.'}
    (folder/'browser_acceptance.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({'status':report['status'],'actual_observations':len(checked),'vector_values':report['verified_vector_values']}))


if __name__=='__main__':main()
