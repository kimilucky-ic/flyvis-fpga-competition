"""Read accepted source arrays, test presenter values with Node; no model/device launch."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import tempfile
from data_store import DataStore, ROOT

parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args()
store = DataStore()
assert not store.errors, store.errors
d = store.datasets['edge24']
cases = []
for angle, intensity, cell in [(60, 1, 'T4c'), (90, 0, 'T5c')]:
    index = next(i for i, c in enumerate(d.conditions) if c['angle'] == angle and c['intensity'] == intensity)
    cases.append(dict(dataset=dict(id=d.id,cell_types=d.cells,time_s=d.time.tolist(),n_frames=len(d.time)),
                      sample=d.sample(index),activity=d.activity[index].ravel().tolist(),stimulus=True,
                      frame=250,loading=False,intensity=intensity,directions=d.directions(cell,intensity)))
with tempfile.TemporaryDirectory(dir=ROOT/'gui_v1/runtime') as folder:
    fixture=Path(folder)/'accepted_arrays.json'
    fixture.write_text(json.dumps(cases),encoding='utf-8')
    check=subprocess.run(['node',str(ROOT/'gui_v1/test_demo_guide.cjs'),str(fixture)],capture_output=True,text=True,check=True)
    result=json.loads(check.stdout)
result.update(checked_utc=datetime.now(timezone.utc).isoformat(),evidence_level='READ_ONLY_PRESENTATION_TEST',
              datasets={key:len(value.conditions) for key,value in store.datasets.items()},
              source_input_sha256=d.hashes['stimulus.npy'],source_activity_sha256=d.hashes['activity_central.npy'],
              gpu_launched=False,camera_launched=False,board_accessed=False)
Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
