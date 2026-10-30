"""Thin sealed-DDR-record adapter; no hardware imports, writes or neural math.

Call from the existing independent auditor AFTER full-state validation/save.
Physical operator context must be accepted separately before opening GUI ingress.
"""
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys
from types import SimpleNamespace

PROFILE='LINE11_DDR_FP32_ABI_00110004'
BIT_SHA='d365f41da4b52dc8dbd0ba751f8691da448607747a6bcf04e619ab465d956b66'
HWH_SHA='69a4332593e32852aec9dbc7b177341f3303af067ee1f182c44152744f8598f1'
ZIP_SHA='abd5fe7de6e0c769a4a96ff42eaf5a60637ae290dd275f9e71d19ad60393d502'
MANIFEST_SHA='0d9cb412dcb5a37ce32b10341437b57e2171c99c0cc1c78cb6cf107647baadee'
CORE_CYCLES=2199975
COUNTER_DEFINITION='NEURAL_PHASE_EXCLUDING_INPUT_FEED_AND_FINAL_DDR_PUBLICATION'
INITIAL_BOUNDARY='NOT_SUPPORTED_BY_ABI_00110004'
RELEASE=Path(__file__).resolve().parents[2]/'fpga/flyvis-lossless-study/ddr_release_20261018'


def require(ok,message):
    if not ok:raise ValueError(message)


def digest(data):return hashlib.sha256(data).hexdigest()


def verify_release():
    """Read-only package identity; does not run any packaged entrypoint."""
    root=RELEASE/'bundle_r2'
    raw=(root/'release_manifest.json').read_bytes()
    require(digest(raw)==MANIFEST_SHA,'DDR_RELEASE_MANIFEST_CHANGED')
    require(digest((RELEASE/'flyvis_line11_ddr_100mhz_offline_r2.zip').read_bytes())==ZIP_SHA,'DDR_RELEASE_ZIP_CHANGED')
    files=json.loads(raw)
    for name,info in files.items():
        path=(root/name).resolve();require(path.is_relative_to(root.resolve()),'DDR_PACKAGE_PATH')
        data=path.read_bytes();require(len(data)==info['bytes'] and digest(data)==info['sha256'],'DDR_SOURCE_CHANGED '+name)
    require(files['flyvis_ddr.bit']['sha256']==BIT_SHA and files['flyvis_ddr.hwh']['sha256']==HWH_SHA,'DDR_IMAGE_PROFILE')
    return root,files


def record_codec(root,files):
    """Import only the reviewed SHA-bound stdlib codec, never the launcher."""
    path=Path(root)/'snapshot_records.py'
    raw=path.read_bytes();require(digest(raw)==files['snapshot_records.py']['sha256'],'DDR_CODEC_CHANGED')
    name='_line2_ddr_codec_'+digest(raw)[:16]
    if name not in sys.modules:
        spec=importlib.util.spec_from_file_location(name,path)
        module=importlib.util.module_from_spec(spec);sys.modules[name]=module
        spec.loader.exec_module(module)
    return sys.modules[name]


def check_receipt(row,frame,run_id,cookie,previous_chain,input_sha,state_sha):
    require(row['run_id']==run_id and row['cookie']==cookie and row['frame_id']==frame,'DDR_AUDIT_RUN_OR_STEP')
    require(row['board_result'] is False,'DDR_DO_NOT_PROMOTE_UNATTESTED_RECEIPT')
    require(row['input_sha256']==input_sha and row['state_sha256']==state_sha,'DDR_AUDIT_ARRAY_IDENTITY')
    require(row['previous_chain']==previous_chain and row['record_bytes']==188416,'DDR_AUDIT_CHAIN')
    expected=digest(bytes.fromhex(previous_chain)+struct.pack('<I',frame)+bytes.fromhex(input_sha)+bytes.fromhex(state_sha))
    require(row['chain']==expected,'DDR_AUDIT_CHAIN_DIGEST')
    require(isinstance(row['record_sha256'],str) and len(bytes.fromhex(row['record_sha256']))==32,'DDR_RAW_RECORD_IDENTITY')


class DdrAuditForwarder:
    """Forward every audited record; the ORIGINAL GUI draws latest-only."""
    def init__(self,client,cookie,first_receipt):
        config=client.config
        require(config.get('transport_profile')==PROFILE,'DDR_REQUIRES_DDR_GUI_ADMISSION')
        require(first_receipt['run_id']==config['run_id'] and first_receipt['cookie']==cookie
                and first_receipt['frame_id']==0 and first_receipt['state_sha256']==config['seed_state_sha256'],'DDR_FIRST_RECORD_BINDING')
        require(config.get('initial_state_readback')==INITIAL_BOUNDARY,'DDR_INITIAL_BOUNDARY')
        self.client,self.cookie=client,cookie
        self.previous=first_receipt['chain'];self.next_frame=1;self.failed=False
        self.evidence='CPU_MOCK_ONLY' if config.get('protocol_test') else 'OPERATOR_PHYSICAL_READS_UNATTESTED'
        require(first_receipt['evidence']==self.evidence,'DDR_EVIDENCE_MISMATCH')

    def publish(self,record,receipt,elapsed_seconds):
        require(not self.failed,'DDR_FORWARDER_FAILED_NO_RETRY')
        try:
            inp,state=bytes(record.input_bits),bytes(record.state_bits)
            require(len(inp)==2884 and len(state)==182676 and record.cycles==CORE_CYCLES,'DDR_FULL_RECORD_REQUIRED')
            require(record.frame_id==self.next_frame and receipt['evidence']==self.evidence,'DDR_FORWARD_ORDER_OR_EVIDENCE')
            require(type(elapsed_seconds) in (int,float) and math.isfinite(elapsed_seconds) and elapsed_seconds>=0,'DDR_MEASURED_ELAPSED_REQUIRED')
            check_receipt(receipt,record.frame_id,self.client.config['run_id'],self.cookie,self.previous,digest(inp),digest(state))
            frame=SimpleNamespace(frame_id=record.frame_id,completed_steps=record.frame_id+1,input_bits=inp,state_bits=state,
                compute_cycles=record.cycles,elapsed_seconds=elapsed_seconds,transport_profile=PROFILE,source_audit=dict(receipt))
            self.client(frame)
            self.previous=receipt['chain'];self.next_frame+=1
        except Exception:
            self.failed=True;raise
