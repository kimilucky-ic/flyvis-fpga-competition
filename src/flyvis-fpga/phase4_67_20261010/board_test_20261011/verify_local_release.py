"""Read files only; never import PYNQ or access hardware."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(release):
    manifest = json.loads((release / 'release_manifest.json').read_text(encoding='utf-8'))
    checks = []
    for key in ('bitstream', 'hwh', 'xsa'):
        entry = manifest['files'][key]
        path = release / entry['path']
        checks.append({'file': entry['path'], 'sha256': digest(path),
                       'matches_manifest': digest(path) == entry['sha256']})
    for entry in manifest['copied_vectors'].values():
        path = release / entry['path']
        checks.append({'file': entry['path'], 'sha256': digest(path),
                       'matches_manifest': digest(path) == entry['sha256']})
    root = ET.parse(release / manifest['files']['hwh']['path']).getroot()
    modules = list(root.iter('MODULE'))
    hls = next(m for m in modules if m.get('INSTANCE') == 'flyvis_h')
    ps = next(m for m in modules if m.get('MODTYPE') == 'processing_system7')
    ranges = [m.attrib for m in root.iter('MEMRANGE')
              if m.get('INSTANCE') == 'flyvis_h' and m.get('ADDRESSBLOCK') == 'Reg']
    assert len(ranges) == 1, 'Expected one HLS register memory range'
    assert ranges[0]['BASEVALUE'].lower() == '0x43c00000'
    assert ranges[0]['HIGHVALUE'].lower() == '0x43c0ffff'
    registers = {}
    for reg in hls.findall('./ADDRESSBLOCKS/ADDRESSBLOCK/REGISTERS/REGISTER'):
        props = {p.get('NAME'): p.get('VALUE') for p in reg.findall('./PROPERTY')}
        registers[reg.get('NAME')] = {'offset': int(props['ADDRESS_OFFSET']),
                                    'size_bits': int(props['SIZE'])}
    assert registers == manifest['control_register_map']['control_registers'], 'Register ABI mismatch'
    params = {p.get('NAME'): p.get('VALUE') for p in ps.findall('./PARAMETERS/PARAMETER')}
    clocks = [p.attrib for p in ps.findall('./PORTS/PORT') if p.get('NAME') == 'FCLK_CLK0']
    assert clocks and int(clocks[0]['CLKFREQUENCY']) == 100000000
    assert params.get('PCW_S_AXI_HP0_DATA_WIDTH') == '64'
    names = ['PCW_UIPARAM_DDR_PARTNO', 'PCW_UIPARAM_DDR_BUS_WIDTH',
             'PCW_S_AXI_HP0_DATA_WIDTH', 'PCW_PRESET_BANK0_VOLTAGE',
             'PCW_PRESET_BANK1_VOLTAGE']
    names += ['PCW_MIO_%d_IOTYPE' % i for i in range(16, 28)]
    vendor = json.loads((Path(__file__).parents[1] / 'artifacts/LEADER_PS7_USER_PARAMS.json').read_text(encoding='utf-8'))
    mismatches = [{'name': n, 'vendor_reference': vendor.get(n), 'generated_hwh': params.get(n)}
                  for n in names if vendor.get(n) != params.get(n)]
    assert all(c['matches_manifest'] for c in checks), 'Release integrity mismatch'
    return {'status': 'PASS_LOCAL_FILES_HASH_HWH_ABI_ONLY', 'board_io_operations': 0,
            'evidence_level': 'LOCAL_FILES_ONLY_NO_LIVE_BOARD_RUNTIME',
            'checks': checks, 'hls_vlnv': hls.get('VLNV'), 'control_range': ranges[0],
            'control_registers': registers, 'fclk0': clocks[0],
            'ps7_reference_parameters': {n: params.get(n) for n in names},
            'generated_vs_vendor_parameter_mismatches': mismatches,
            'driver_sha256': digest(Path(__file__).parents[1] / 'pynq/flyvis_v1_driver.py'),
            'physical_board': {'presence': 'USER_REPORTED_AT_HAND',
                               'power': 'USER_REPORTED_NOT_POWERED',
                               'revision': None, 'ddr_part': None, 'pynq_version': None},
            'driver_evidence_audit': {'full_register_trace': 'NOT_IMPLEMENTED_IN_ORIGINAL_DRIVER',
                                     'elapsed_time': 'NOT_RECORDED_IN_ORIGINAL_DRIVER',
                                     'timeout_buffer_lifetime': 'REQUIRES_FIX_BEFORE_BOARD_RUN'},
            'first_load_gate': 'CLOSED_PENDING_PHYSICAL_REVIEW_AND_EXACT_USER_AUTHORIZATION'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = inspect(args.release_dir)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
