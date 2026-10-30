"""Exercise actual embedded Notebook up to a fake board entry, CPU only."""
import builtins
import importlib
import io
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import urllib.request
import uuid

HERE=Path(__file__).resolve().parents[2];sys.path.insert(0,str(HERE))
import ov5640_adapter as ov
from ov5640_notebook import export_notebook
ROOT=Path(__file__).resolve().parent/('notebook_cpu_'+uuid.uuid4().hex[:8]);ROOT.mkdir()
saved_open=urllib.request.urlopen;saved_import=importlib.import_module;saved_input=builtins.input;saved_cwd=Path.cwd()
scope={};exec((ov.BUNDLE/'gui_conditions.py').read_text(),scope)
rows=[]
try:
    for answer in ('同意单帧测试','取消'):
        s=ov.OV5640Session(ROOT/'sessions')
        folder=ROOT/s.session_id;folder.mkdir();os.chdir(folder)
        notebook=export_notebook('http://192.168.2.89:8771',folder)
        code=''.join(json.loads(notebook.read_text())['cells'][1]['source'])
        calls=[]
        def urlopen(request,timeout):
            assert request.full_url.endswith('/api/full-pl-stream/notebook-bundle')
            body=json.loads(request.data);calls.append(body['kind'])
            result=s.notebook_bundle(body,request.get_header('Authorization'))
            return io.BytesIO(result if isinstance(result,bytes) else json.dumps(result).encode())
        def board_run(parent,conditions,*,authorize_load_and_one_step):
            calls.append('FAKE_BOARD_ENTRY')
            assert authorize_load_and_one_step and conditions['operator_confirmation']=='同意单帧测试'
            assert conditions['SCCB_pullups_voltage_and_rise_time_checked'] is False
            assert conditions['physical_clock_measured'] is False
            assert conditions['baseboard_revision']=='V3.9'
            raise RuntimeError('CPU_TEST_STOP_BEFORE_REAL_BOARD')
        fake=SimpleNamespace(check_conditions=scope['check_conditions'],run=board_run)
        urllib.request.urlopen=urlopen
        importlib.import_module=lambda name:fake if name=='board_capture' else saved_import(name)
        builtins.input=lambda _:answer
        try:exec(compile(code,'EXPORTED_NOTEBOOK_CPU_ONLY','exec'),{})
        except RuntimeError as e:assert str(e)=='CPU_TEST_STOP_BEFORE_REAL_BOARD' and answer=='同意单帧测试'
        except AssertionError as e:assert answer=='取消' and str(e)=='未授权；无加载/采集/神经计算'
        else:raise AssertionError('Should stop at fake entry or decline')
        assert calls==(['manifest','package','capture-intent','FAKE_BOARD_ENTRY'] if answer=='同意单帧测试' else ['manifest','package'])
        assert s.claimed==(answer=='同意单帧测试')
        rows.append(dict(answer=answer,calls=calls,real_hardware_calls=0))
finally:
    urllib.request.urlopen=saved_open;importlib.import_module=saved_import;builtins.input=saved_input;os.chdir(saved_cwd)
assert 'pynq' not in sys.modules
report=dict(status='PASS_EXPORTED_NOTEBOOK_CPU_MOCK_ONLY',cases=rows,board_operations=0)
(ROOT/'RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
