"""Independently check recorded actual UI observations and actual exported CSV."""
import csv
from datetime import datetime,timezone
import json
from pathlib import Path

from data_store import DataStore,ROOT,read_json,sha256,TARGETS
from phase3_adapter import Phase3Adapter


def main():
    evidence=ROOT/'gui_v1/evidence/phase3';s=Phase3Adapter(DataStore());assert not s.errors
    p=next(iter(s.packages.values()));f=p.frozen
    observed=read_json(evidence/'browser_observations.json')
    count=0
    for row in observed['observations']:
        mode='Python_Replacement' if row['execution'].startswith('Python') else 'Full_GPU';k=row['frame']
        assert not row['errorVisible'] and f'step_id={k} / 799' in row['stepText'] and p.descriptor['modes'][mode]['run_id'] in row['modeText']
        assert row['input']==f'{f.time[k]:.3f} s' and row['activity']==f'{f.activity_time[k]:.3f} s'
        source=int(f.video.source_indices[k]);assert row['source']==f'源帧 {source} / 文件时间 {f.video.source_time[source]:.6f} s'
        for value in row['values']:
            i=f.cells.index(value['cell']);expected=p.arrays[mode][k,f.central_ids[i]]
            assert value['value']==f'{expected:.3f}',(row['tag'],value,expected)
            count+=1
    assert observed['other_condition_python_unavailable'] and observed['edge24_official_DSI_observed']=='0.6274' and observed['flash_observed']=='Flash / ON'
    rows=list(csv.DictReader((evidence/'actual_export_800.csv').open(encoding='utf-8',newline='')));assert len(rows)==800
    for k,row in enumerate(rows):
        assert int(row['step_id'])==k and row['comparison_id']==f.comparison_id and row['display_kind']=='offline_replay'
        assert float(row['input_time_s'])==f.time[k] and float(row['activity_time_s'])==f.activity_time[k]
        source=int(f.video.source_indices[k]);assert int(row['source_frame'])==source and float(row['source_time_s'])==f.video.source_time[source]
        assert row['stimulus_sha256']==f.fingerprint['stimulus'] and row['initial_state_sha256']==f.fingerprint['initial']
        for own,prefix in [('Full_GPU','full'),('Python_Replacement','python')]:
            run=p.descriptor['modes'][own];assert row[prefix+'_run_id']==run['run_id'] and row[prefix+'_activity_sha256']==run['source_activity_sha256']
        for cell in TARGETS:
            i=f.central_ids[f.cells.index(cell)];full=float(p.arrays['Full_GPU'][k,i]);python=float(p.arrays['Python_Replacement'][k,i])
            assert float(row[cell+'_Full'])==full and float(row[cell+'_Python'])==python and float(row[cell+'_Python_minus_Full'])==python-full
    report=dict(schema='flyvis-gui-phase3-actual-browser-acceptance-v1',status='PASS',utc=datetime.now(timezone.utc).isoformat(),comparison_id=f.comparison_id,observations=len(observed['observations']),actual_T4T5_readouts_verified=count,CSV_rows=800,CSV_activity_and_error_values_exact=800*8*3,source_and_double_time_axes_match=True,other_condition_replacement_unavailable=True,official_DSI_preserved=True,Flash_preserved=True,FPGA_unavailable=True,GPU_submit_not_connected=True,display_kind='offline_replay_of_actual_A_B_computation',observations_sha256=sha256(evidence/'browser_observations.json'),CSV_sha256=sha256(evidence/'actual_export_800.csv'),FPGA_execution=False)
    (evidence/'browser_acceptance.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))


if __name__=='__main__':main()
