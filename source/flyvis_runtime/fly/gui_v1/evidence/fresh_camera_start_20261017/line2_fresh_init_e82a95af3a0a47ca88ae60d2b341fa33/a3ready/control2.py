"""Control helpers: no CUDA, PYNQ, network or subprocess activity on import."""
import hashlib
import hmac
import json
import os
from pathlib import Path
import uuid

BIT_SHA = 'b607ea58005046f09f01bc7359c673dbd5e40b4de12b4169fca79ce88e43fd16'
HWH_SHA = '54d271dc8aff904a50ca4fb0ff433f1810b0d486cf80f1daed2c204bc88d084c'
NUMERIC_DRIVER_SHA = 'e2c34f5b5a14aee8c02640f572850792ae6d2e10cc646e3427165f1f3be19f68'
OLD_RUNS = {'6b97fe302e34421f9c123fd991a8cf10', '759c9f469bf84760b57dcb9daa583f1b',
            'af3345a51c5c455798392b9efeada847', '144df2ff2c8e46ef82886bfb8572fed4',
            '496b7c0b852b422e92cd68ede47fa3a7'}
OLD_SESSIONS = {'098e06fe3a07483c859db130391625be', 'f6f0fc75d3304655adc9c9879be0249b',
                'be0fe93cfc4d459f9aaeab5011c5f324', '2b74c882a040447db1dd1fb5b3dd098e',
                '41cc4b8f429b49cca9a972736006886a', 'b1886f1c4602433e9c6d7cce21c10aab'}
IDENTITY_KEYS = ('run_id', 'server_session', 'boot_id', 'scope_sha256', 'listener_id')

def require(condition, message):
    if not condition:
        raise ValueError(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def encoded_record(value):
    # Exact parity with the unchanged line2 native Windows writer.
    raw = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False)
    return raw.replace('\n', '\r\n').encode('utf-8') if os.name == 'nt' else raw.encode('utf-8')

def write_once(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.pending-' + uuid.uuid4().hex)
    with temporary.open('xb') as stream:
        stream.write(encoded_record(value)); stream.flush(); os.fsync(stream.fileno())
    try:
        if os.name == 'nt':
            os.rename(temporary, path)
        else:
            os.link(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()

def sign(body, key):
    return dict(body=body, mac=hmac.new(bytes.fromhex(key), canonical(body), hashlib.sha256).hexdigest())

def verified(packet, key):
    require(isinstance(packet, dict) and set(packet) == {'body', 'mac'}, 'MALFORMED_ENVELOPE')
    require(isinstance(packet['mac'], str) and hmac.compare_digest(sign(packet['body'], key)['mac'], packet['mac']), 'BAD_HMAC')
    return packet['body']

def fresh_ids(run, session):
    require(uuid.UUID(hex=run).hex == run and uuid.UUID(hex=session).hex == session, 'BAD_UUID')
    require(run not in OLD_RUNS and session not in OLD_SESSIONS, 'OLD_RUN_OR_SESSION')

def same_identity(body, identity):
    require(all(body.get(k) == identity[k] for k in IDENTITY_KEYS), 'WRONG_IDENTITY')
