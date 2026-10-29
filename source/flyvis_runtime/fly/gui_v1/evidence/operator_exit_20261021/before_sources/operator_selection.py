"""Selection/launch handoff for the ORIGINAL GUI and its two controllers.

No neural implementation or board access. The optional main is a foreground
launcher; it waits for normal close, never kills/retries an existing run.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

HERE=Path(__file__).resolve().parent


def validate(value, conditions):
    if not isinstance(value,dict) or set(value)!={'backend','input','condition'}:
        raise ValueError('SELECT_EXACT_FIELDS')
    if value['backend'] not in ('GPU_FPGA','FULL_FPGA') or value['input'] not in ('camera','scientific28'):
        raise ValueError('SELECT_BACKEND_OR_INPUT')
    if value['input']=='camera':
        if value['condition'] is not None:raise ValueError('CAMERA_HAS_NO_FROZEN_CONDITION')
    elif value['condition'] not in conditions:raise ValueError('SELECT_UNKNOWN_CONDITION')
    return dict(value)


def command(selection,stop):
    """Build argv only. Caller explicitly chooses whether to launch anything."""
    if selection is None:
        return [sys.executable,'-B',str(HERE/'server.py'),'--stop-file',str(stop)]
    v=selection
    if v['backend']=='GPU_FPGA':
        args=[sys.executable,'-B',str(HERE/'joint_camera_controller.py'),'--workbench','--fixed-notebook','--execute','--operator-stop',str(stop)]
        if v['input']=='scientific28':args+=['--scientific-condition',v['condition']]
        return args
    args=[sys.executable,'-B',str(HERE/'server.py'),'--line11-ddr','--line11-steps','485',
          '--line11-pc-address','192.168.2.89','--line11-live-camera','--stop-file',str(stop),'--no-open']
    if v['input']=='scientific28':args+=['--scientific-condition',v['condition']]
    return args


class Selection:
    def init__(self,root,source_factory=None):
        self.root=Path(root).resolve() if root else None
        self.factory=source_factory
        self.source=None

    def catalogue(self):
        if self.source is None:
            if self.factory:self.source=self.factory()
            else:
                from controlled_stimuli28 import ControlledStimuli28
                self.source=ControlledStimuli28(results_config=False)
        return self.source.metadata_input()

    def status(self):
        p=self.root/'CURRENT.json' if self.root else None
        return dict(managed=self.root is not None,selection=json.loads(p.read_text()) if p and p.exists() else None,
            catalogue=self.catalogue(),FPGA_status='NOT_CONNECTED',actual_execution=False,
            meaning='Selection is not board preparation or computation')

    def select(self,value,*,busy=False):
        if self.root is None:raise ValueError('OPEN_FIXED_OPERATOR_ENTRY_FIRST')
        if busy:raise ValueError('STOP_AND_FINISH_AUDIT_BEFORE_SWITCH')
        v=validate(value,self.catalogue_condition_ids())
        self.root.mkdir(parents=True,exist_ok=True)
        target=self.root/'NEXT.json'
        with target.open('x',encoding='utf-8') as f:json.dump(v,f)
        return dict(status='SWITCH_AFTER_NORMAL_CLOSE',selection=v,actual_execution=False)

    def catalogue_condition_ids(self):
        return {c['condition_id'] for c in self.catalogue()['conditions']}


def main():
    """One fixed PC entry, same existing GUI, cooperative close only."""
    from launch_recovery import gui_port_available
    gui_port_available()
    parent=HERE/'runtime/operator';parent.mkdir(parents=True,exist_ok=True)
    selected=None
    while True:
        root=parent/uuid.uuid4().hex;root.mkdir()
        if selected is not None:(root/'CURRENT.json').write_text(json.dumps(selected),encoding='utf-8')
        env=dict(os.environ,FLYVIS_OPERATOR_ROOT=str(root),FLYVIS_OPERATOR_STOP=str(root/'STOP.json'))
        with (root/'backend.log').open('xb') as log:
            child=subprocess.Popen(command(selected,root/'STOP.json'),cwd=str(HERE),env=env,stdout=log,stderr=subprocess.STDOUT)
            code=child.wait()
        request=root/'NEXT.json'
        if code!=0:raise RuntimeError('所选实验未正常结束；不自动重试。请查看 '+str(root/'backend.log'))
        if not request.exists():return 0
        # Revalidate after normal process exit; never replay an old next request.
        selected=validate(json.loads(request.read_text()),Selection(root).catalogue_condition_ids())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Original FlyVis input/backend selector')
    parser.add_argument('--run',action='store_true')
    if not parser.parse_args().run:parser.error('Use the fixed PC entry')
    try:raise SystemExit(main())
    except Exception as error:
        report=HERE/'runtime/operator_launch_error.json';report.parent.mkdir(parents=True,exist_ok=True)
        report.write_text(json.dumps(dict(error=str(error),automatic_retry=False),ensure_ascii=False),encoding='utf-8')
        if os.name=='nt':
            import ctypes
            ctypes.windll.user32.MessageBoxW(0,str(error)+'\n'+str(report),'FlyVis 实验台',16)
        raise
