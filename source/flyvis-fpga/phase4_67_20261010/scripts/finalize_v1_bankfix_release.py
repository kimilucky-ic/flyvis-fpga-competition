"""Seal a new bank-corrected full SoC release; no board I/O or old-file writes."""
import argparse
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from finalize_v1_release import ROOT, P3, HLS, COMPONENT, FIXTURE, sha, register_map, timing_extract, copy_or_verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-dir', required=True, type=Path)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--vivado-log', required=True, type=Path)
    parser.add_argument('--source-review', required=True, type=Path)
    args = parser.parse_args()
    release, build, log = args.release_dir.resolve(), args.build_dir.resolve(), args.vivado_log.resolve()
    if not release.name.startswith('V1_bankfix_') or not (build / 'flyvis67v1.xpr').is_file():
        raise ValueError('Expected a new bankfix release and its isolated full SoC project')
    if (release / 'release_manifest.json').exists():
        raise FileExistsError('Refusing to overwrite a sealed release manifest')
    raw_log = log.read_text(encoding='utf-8', errors='replace')
    normalize = lambda p: str(p).replace('\\', '/').lower()
    if ('FLYVIS_V1_SOC_IMPL_BIT_HWH_READY' not in raw_log
            or 'build=' + normalize(build) not in raw_log.lower()
            or 'release=' + normalize(release) not in raw_log.lower()):
        raise ValueError('Completion log does not identify this exact build and release')
    if re.search(r'^ERROR:', raw_log, re.MULTILINE) or 'PS7-6' in raw_log:
        raise ValueError('Vivado error or unresolved PS7-6 in completion log')
    keys = {
        'bitstream': 'flyvis_t5c_source_raw_v1.bit', 'hwh': 'flyvis_t5c_source_raw_v1.hwh',
        'xsa': 'flyvis_t5c_source_raw_v1.xsa',
        'implementation_timing': 'implementation_timing_summary.rpt',
        'implementation_utilization': 'implementation_utilization.rpt',
        'implementation_drc': 'implementation_drc.rpt', 'implementation_io': 'implementation_io.rpt',
        'synthesis_timing': 'synth_timing_summary.rpt', 'synthesis_utilization': 'synth_utilization.rpt'}
    files = {}
    for key, name in keys.items():
        path = release / name
        if not path.is_file():
            raise FileNotFoundError(path)
        files[key] = {'path': name, 'bytes': path.stat().st_size, 'sha256': sha(path)}
    timing = timing_extract(release / keys['implementation_timing'])
    if not timing.get('all_setup_and_hold_constraints_met'):
        raise ValueError('Full SoC timing did not pass')
    timing_text = (release / keys['implementation_timing']).read_text(encoding='utf-8')
    for check in ('no_clock', 'unconstrained_internal_endpoints'):
        counts = re.findall(r'checking ' + check + r' \((\d+)\)', timing_text)
        if not counts or any(int(c) != 0 for c in counts):
            raise ValueError('Missing/failed internal timing coverage check: ' + check)
        timing[check] = 0
    drc_text = (release / keys['implementation_drc']).read_text(encoding='utf-8')
    drc_rows = re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*(Warning|Error|Critical Warning)\s*\|[^\n]*?\|\s*(\d+)\s*\|', drc_text, re.MULTILINE)
    if any(severity != 'Warning' for _, severity, _ in drc_rows):
        raise ValueError('Full SoC DRC contains error or critical-warning checks')
    if 'REPORT SUMMARY' not in drc_text or 'Fully Routed' not in drc_text:
        raise ValueError('Wrong DRC report stage')
    drc = {'error_checks': 0, 'warning_checks': sum(int(n) for _, _, n in drc_rows),
           'rules': [{'rule': rule, 'severity': severity, 'checks': int(n)} for rule, severity, n in drc_rows]}
    utilization_text = (release / keys['implementation_utilization']).read_text(encoding='utf-8')
    if not re.search(r'\| Design State\s*:\s*(?:Fully )?Routed\s*$', utilization_text, re.MULTILINE) or 'xc7z020clg400-2' not in utilization_text:
        raise ValueError('Wrong utilization report stage/device')
    resources = {}
    for label in ('Slice LUTs', 'Slice Registers', 'Block RAM Tile', 'DSPs'):
        match = re.search(r'^\|\s*' + re.escape(label) + r'\*?\s*\|\s*([\d.]+)\s*\|', utilization_text, re.MULTILINE)
        if not match:
            raise ValueError('Missing routed utilization row: ' + label)
        resources[label] = float(match.group(1))
    hwh = ET.parse(release / keys['hwh']).getroot()
    ps = [m for m in hwh.iter('MODULE') if m.get('MODTYPE') == 'processing_system7']
    hls = [m for m in hwh.iter('MODULE') if m.get('INSTANCE') == 'flyvis_h']
    if len(ps) != 1 or len(hls) != 1 or hls[0].get('VLNV') != 'xilinx.com:hls:flyvis_t5c_source_raw:1.0':
        raise ValueError('Wrong PS7/HLS identity')
    params = {p.get('NAME'): p.get('VALUE') for p in ps[0].findall('./PARAMETERS/PARAMETER')}
    expected = {'PCW_PRESET_BANK0_VOLTAGE': 'LVCMOS 3.3V',
                'PCW_PRESET_BANK1_VOLTAGE': 'LVCMOS 1.8V',
                'PCW_S_AXI_HP0_DATA_WIDTH': '64', 'PCW_USE_S_AXI_HP0': '1',
                'PCW_CRYSTAL_PERIPHERAL_FREQMHZ': '33.333333',
                'PCW_UIPARAM_DDR_FREQ_MHZ': '533.333333',
                'PCW_UIPARAM_DDR_PARTNO': 'MT41K256M16 RE-125',
                'PCW_UIPARAM_DDR_BUS_WIDTH': '32 Bit'}
    expected.update({'PCW_MIO_%d_IOTYPE' % i: 'LVCMOS 1.8V' for i in range(16, 28)})
    expected.update({'PCW_MIO_%d_IOTYPE' % i: 'LVCMOS 1.8V' for i in (52, 53)})
    for name, value in expected.items():
        if params.get(name) != value:
            raise ValueError('Wrong PS7 parameter: %s actual=%r expected=%r' % (name, params.get(name), value))
    ranges = [n.attrib for n in hwh.iter('MEMRANGE')
              if n.get('INSTANCE') == 'flyvis_h' and n.get('ADDRESSBLOCK') == 'Reg']
    if (len(ranges) != 1 or ranges[0]['BASEVALUE'].lower() != '0x43c00000'
            or ranges[0]['HIGHVALUE'].lower() != '0x43c0ffff'):
        raise ValueError('Wrong HLS control address')
    clocks = [p for p in ps[0].findall('./PORTS/PORT') if p.get('NAME') == 'FCLK_CLK0']
    if len(clocks) != 1 or int(clocks[0].get('CLKFREQUENCY')) != 100000000:
        raise ValueError('Wrong FCLK0')
    old = json.loads((ROOT / 'build/V1_20261010_210347/release_manifest.json').read_text(encoding='utf-8'))
    for entry in old['files']['hls_sources_and_roms']:
        if sha(P3 / entry['path']) != entry['sha256']:
            raise ValueError('Validated HLS source/ROM changed: ' + entry['path'])
    if sha(COMPONENT) != old['files']['hls_component_xml']['sha256']:
        raise ValueError('Validated HLS component changed')
    files['hls_sources_and_roms'] = old['files']['hls_sources_and_roms']
    files['hls_component_xml'] = old['files']['hls_component_xml']
    p3_evidence = json.loads((P3 / 'artifacts/BUILD_EVIDENCE_REPORT.json').read_text(encoding='utf-8'))
    rtl_checks = []
    for path_text, digest in p3_evidence['hls_rtl_ooc']['source_sha256'].items():
        path = Path(path_text)
        if sha(path) != digest:
            raise ValueError('Validated HLS OOC source changed: ' + path_text)
        entry = {'path': path_text, 'sha256': digest}
        if path.parent.name == 'hdl' and path.name != 'clockinfo.txt':
            matches = [p for p in (HLS / 'hdl').rglob(path.name) if 'verilog' in p.parts]
            if len(matches) != 1 or sha(matches[0]) != digest:
                raise ValueError('Actual synthesis IP Verilog/ROM does not match validated OOC source: ' + path.name)
            entry['ip_verilog_files'] = [{'path': str(p), 'sha256': sha(p)} for p in matches]
        rtl_checks.append(entry)
    vectors = release / 'vectors'
    vectors.mkdir(exist_ok=True)
    vector_entries = {}
    for name in ('requests_i32le.bin', 'expected_i32le.bin', 'fixture_manifest.json', 'request_map.csv'):
        entry = copy_or_verify(FIXTURE / name, vectors / name)
        vector_entries[name] = {**entry, 'path': 'vectors/' + name}
    fixture = json.loads((vectors / 'fixture_manifest.json').read_text(encoding='utf-8'))
    if fixture['comparison_id'] != old['fixture_identity']['comparison_id']:
        raise ValueError('Fixture comparison identity changed')
    logs = release / 'logs'
    logs.mkdir(exist_ok=True)
    log_entries = {}
    for name, path in {'vivado_full_soc.log': log,
                       'synth_1_runme.log': build / 'flyvis67v1.runs/synth_1/runme.log',
                       'impl_1_runme.log': build / 'flyvis67v1.runs/impl_1/runme.log'}.items():
        entry = copy_or_verify(path, logs / name)
        log_entries[name] = {**entry, 'path': 'logs/' + name}
    source_files = [args.source_review.resolve(), ROOT / 'artifacts/LEADER_BOARD_REFERENCE_AUDIT.json',
                    ROOT / 'artifacts/LEADER_PS7_USER_PARAMS.json',
                    ROOT / 'artifacts/leader_ps7_user_params.tcl',
                    ROOT / 'scripts/build_v1_soc_bankfix.tcl', ROOT / 'scripts/run_v1_soc_bankfix.ps1',
                    Path(__file__).resolve(), ROOT / 'scripts/finalize_v1_release.py']
    source_dir = release / 'source_identity'
    source_dir.mkdir(exist_ok=True)
    source_entries = []
    for path in source_files:
        entry = copy_or_verify(path, source_dir / path.name)
        source_entries.append({**entry, 'path': 'source_identity/' + path.name, 'original_path': str(path)})
    software_dir = release / 'pynq'
    software_dir.mkdir(exist_ok=True)
    software_entries = {}
    for name in ('first_board_step.py', 'flyvis_v1_evidence_driver.py', 'flyvis_v1_driver.py'):
        entry = copy_or_verify(ROOT / 'pynq' / name, software_dir / name)
        software_entries[name] = {**entry, 'path': 'pynq/' + name}
    manifest = {
        'status': 'FULL_SOC_BIT_HWH_READY_BOARD_NOT_AUTHORIZED',
        'evidence_level': 'VIVADO_FULL_SOC_IMPLEMENTATION_AND_BITSTREAM; NO_LIVE_BOARD_EXECUTION',
        'target': 'xc7z020clg400-2', 'tool': 'Vivado 2026.1.1 build 6605303',
        'design': 'FlyVis T5c 67 nodes SOURCE_RAW Q22, unchanged validated HLS V1',
        'build_project': str(build), 'files': files, 'build_logs': log_entries,
        'source_identity': source_entries, 'unchanged_hls_ooc_sources': rtl_checks,
        'first_step_software': software_entries,
        'control_register_map': register_map(),
        'interfaces': {'PS_M_AXI_GP0': 'AXI-Lite control',
                       'PS_S_AXI_HP0': 'HLS m_axi DDR master, 64-bit HP0; no AXI DMA engine',
                       'FCLK0_Hz': 100000000},
        'hwh_instances': {'processing_system7': ps[0].attrib, 'flyvis_h': hls[0].attrib},
        'ps7_checked_parameters': expected, 'ps7_6_warning_present': False,
        'timing': timing, 'drc': drc, 'routed_resources': resources, 'copied_vectors': vector_entries,
        'fixture_identity': dict(old['fixture_identity']),
        'first_operation_scope': {'row': 0, 'requests': 1, 'commit': False, 'true_closed_loop': False},
        'board_programming': 'NOT_PERFORMED; exact user authorization and physical/runtime precheck pending'}
    with (release / 'release_manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': manifest['status'], 'release': str(release), 'timing': timing,
                      'bit_sha256': files['bitstream']['sha256'], 'hwh_sha256': files['hwh']['sha256'],
                      'board_io_operations': 0}, indent=2))


if __name__ == '__main__':
    main()
