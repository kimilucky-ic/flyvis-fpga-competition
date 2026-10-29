"""Seal local preparation evidence; no board I/O, no personal memory writes."""
import ast
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
P4 = HERE.parent
WORKSPACE = P4.parent.parent


def identify(path):
    return {'path': str(path.resolve()), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    local = [HERE / 'REFERENCE_REUSE_AUDIT.md', HERE / 'LOCAL_PREFLIGHT.json',
             HERE / 'PS7_BANK_IMPORT_PROBE_20261011_151445.tsv',
             HERE / 'ps7_probe_20261011_151438.log',
             HERE / 'ps7_probe_20261011_151438.console.log',
             HERE / 'ps7_probe_20261011_151159.log',
             HERE / 'ps7_probe_20261011_151305.log',
             HERE / 'probe_ps7_bank_import.tcl', HERE / 'run_ps7_probe.ps1',
             HERE / 'read_only_board_probe.py', HERE / 'check_evidence_driver_software.py',
             HERE / 'MOCK_DRIVER_CHECK_20261011_151809/SOFTWARE_REPORT.json',
             HERE / 'EVIDENCE_DRIVER_SOFTWARE_FINAL.console.log',
             HERE / 'vendor_pynq_guide_extract.txt',
             HERE / 'VENDOR_HARDWARE_GUIDE_EXTRACT.json',
             P4 / 'pynq/flyvis_v1_evidence_driver.py',
             P4 / 'scripts/build_v1_soc_bankfix.tcl', P4 / 'scripts/run_v1_soc_bankfix.ps1']
    local.extend(sorted((HERE / 'MOCK_DRIVER_CHECK_20261011_151809').rglob('register_trace.jsonl')))
    local.extend(sorted((HERE / 'MOCK_DRIVER_CHECK_20261011_151809').rglob('step_report.json')))
    for path in (P4 / 'pynq/flyvis_v1_evidence_driver.py', HERE / 'read_only_board_probe.py'):
        ast.parse(path.read_text(encoding='utf-8'), feature_version=(3, 8))
    source_paths = [WORKSPACE / 'docs/board_cascade_validation_status.md',
                    WORKSPACE / 'docs/fly-Zynq-移植进度报告-2026-10-06.md',
                    WORKSPACE / 'docs/fly-Zynq7020-current-status.md',
                    WORKSPACE / 'external/snn-accelerator/outputs/atk7020_snn_ascii/snn_integrated_v2.bit',
                    WORKSPACE / 'external/snn-accelerator/outputs/atk7020_snn_ascii/snn_integrated_v2.hwh',
                    P4 / 'artifacts/leader_ps7_user_params.tcl']
    primary_root = Path('D:/BaiduNetdiskDownload/正点原子')
    source_paths.extend([primary_root / '2_文档教程/5_【正点原子】领航者ZYNQ之PYNQ开发指南_V3.2.pdf',
                         primary_root / '2_文档教程/1_【正点原子】领航者ZYNQ之FPGA开发指南V3.4.pdf',
                         primary_root / '3_开发板原理图和硬件相关文件/硬件相关文件/开发板规格书/【正点原子】领航者ZYNQ开发板规格书V1.2.pdf'])
    report = {'status': 'LOCAL_PREPARATION_RECORDED_FIRST_LOAD_GATE_CLOSED',
              'board_io_operations': 0, 'board_power': 'USER_REPORTED_NOT_POWERED',
              'checks': {'ps7_bank_import': 'PASS_LOCAL_CONFIGURATION_REPRODUCTION_ONLY',
                         'driver_fault_paths': 'PASS_15_SOFTWARE_SUBSTITUTE_CHECKS_NO_PL_COMPUTE',
                         'python38_syntax': 'PASS_AST_ONLY_NOT_LIVE_PYNQ_COMPATIBILITY'},
              'corrected_full_soc_release': 'NOT_BUILT',
              'source_inventory': [identify(path) for path in source_paths],
              'preparation_evidence': [identify(path) for path in local],
              'skills_reused': ['zynq-7000-board-operations', 'fpga-board-reference-research',
                                'vivado-vitis-toolchain-debugging', 'windows-fpga-path-diagnostics', 'pdf'],
              'skill_capture': 'No new Skill authored; PS7 procedure has one fresh local paired reproduction, no cross-board claim',
              'pending': ['physical revision and power label', 'existing image/PYNQ/HP0 live checks',
                          'corrected full-SoC release and SHA review', 'exact approved first-step launcher',
                          'specific load plus one-step authorization', 'real PL parity and unedited video']}
    destination = HERE / 'PREPARATION_EVIDENCE_MANIFEST.json'
    with destination.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print('LOCAL_PREPARATION_EVIDENCE_SEALED', str(destination.resolve()))
    print('BOARD_IO=0; CORRECTED_FULL_SOC_NOT_BUILT; LIVE_PL_PASS=NONE')


if __name__ == '__main__':
    main()
