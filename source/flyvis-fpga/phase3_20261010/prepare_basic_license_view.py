"""Select a supplied, existing Basic entitlement; never change signed records.

Private output is excluded from publication. No license text/signatures are logged.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


def sha(value):
    return hashlib.sha256(value).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parent
    source = args.source.resolve()
    original = source.read_bytes()
    lines = original.splitlines(keepends=True)
    retained = []
    removed = 0
    basic_records = []
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(rb'\s*(INCREMENT|FEATURE|PACKAGE)\s+(\S+)\s+', line)
        record = [line]
        i += 1
        if match:
            while record[-1].rstrip(b'\r\n').rstrip().endswith(b'\\') and i < len(lines):
                record.append(lines[i]); i += 1
            block = b''.join(record)
            if match[2] == b'Vivado_Alveo_Package':
                removed += 1
                continue
            if match[2] == b'Vivado_Basic_Package':
                basic_records.append(block)
        retained.extend(record)
    if not basic_records or not removed:
        raise ValueError('Expected existing Basic and Alveo entitlement records')
    view = b''.join(retained)
    if any(block not in view for block in basic_records):
        raise ValueError('Basic signed record changed')
    if source.read_bytes() != original:
        raise RuntimeError('Source license changed during preparation')
    directory = root/'build/private_license'
    directory.mkdir(parents=True, exist_ok=True)
    target = directory/'Xilinx_basic.lic'
    if target.exists() and target.read_bytes() != view:
        raise FileExistsError('Different private license view already exists; not overwriting')
    if not target.exists():
        target.write_bytes(view)
    report = {'source_path': str(source), 'source_sha256': sha(original),
              'private_view_path': str(target), 'private_view_sha256': sha(view),
              'removed_alveo_records': removed, 'basic_signed_records_unchanged': True,
              'signed_records_modified': 0, 'scope': 'process-local use; original unchanged; no global license installation'}
    (root/'artifacts/license_view_metadata.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
