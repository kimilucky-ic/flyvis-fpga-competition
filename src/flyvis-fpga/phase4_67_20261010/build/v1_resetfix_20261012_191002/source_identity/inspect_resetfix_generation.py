"""Static old/new reset evidence. No simulator or board access."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT.parent / 'p4b/r20261012_191002'
OLD = ROOT / 'build/v1_bankfix_20261011_153525'
IP = BUILD / 'flyvis67v1.gen/sources_1/bd/flyvis_v1/ip/flyvis_v1_reset_0'
NS = {'s': 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'}


def identity(p):
    return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


old_hwh = ET.parse(OLD / 'flyvis_t5c_source_raw_v1.hwh').getroot()
old_reset = next(m for m in old_hwh.iter('MODULE') if m.get('INSTANCE') == 'reset')
old_params = {p.get('NAME'): p.get('VALUE') for p in old_reset.findall('./PARAMETERS/PARAMETER')}
old_aux = next(p for p in old_reset.findall('./PORTS/PORT') if p.get('NAME') == 'aux_reset_in')
assert old_params['C_AUX_RESET_HIGH'] == '0'
assert old_aux.get('POLARITY') == 'ACTIVE_LOW'
assert [p.attrib for p in old_aux.findall('./CONNECTIONS/CONNECTION')] == [{'INSTANCE': 'zero', 'PORT': 'dout'}]
xml = ET.parse(IP / 'flyvis_v1_reset_0.xml').getroot()
new_values = []
for parameter in xml.findall('.//s:parameter', NS) + xml.findall('.//s:modelParameter', NS):
    name, value = parameter.find('s:name', NS), parameter.find('s:value', NS)
    if name is not None and name.text in ('C_AUX_RESET_HIGH', 'C_EXT_RESET_HIGH'):
        assert value is not None and value.text == '1'
        new_values.append({'name': name.text, 'value': value.text})
assert len(new_values) >= 2
hdl = (IP / 'synth/flyvis_v1_reset_0.vhd').read_text()
assert "C_AUX_RESET_HIGH => '1'" in hdl and "C_EXT_RESET_HIGH => '1'" in hdl
top = (BUILD / 'flyvis67v1.gen/sources_1/bd/flyvis_v1/synth/flyvis_v1.v').read_text()
assert '.aux_reset_in(zero_dout)' in top
old_manifest = json.loads((OLD / 'release_manifest.json').read_text())
for key in ('bitstream', 'hwh'):
    entry = old_manifest['files'][key]
    assert identity(OLD / entry['path'])['sha256'] == entry['sha256']
report = {
    'status': 'PASS_STATIC_GENERATED_RESET_POLARITY_AND_CONNECTION_ONLY',
    'old_aux_reset_high': old_params['C_AUX_RESET_HIGH'], 'old_aux_reset_asserted_by_zero': True,
    'new_reset_parameters': new_values, 'new_aux_zero_connection_present': True,
    'files': [identity(p) for p in (OLD / 'flyvis_t5c_source_raw_v1.hwh', IP / 'flyvis_v1_reset_0.xml',
                                  IP / 'synth/flyvis_v1_reset_0.vhd',
                                  BUILD / 'flyvis67v1.gen/sources_1/bd/flyvis_v1/synth/flyvis_v1.v')],
    'board_execution_proven': False, 'whole_system_failure_cause_proven': False,
    'old_firmware_hashes_unchanged': True, 'corrected_implementation_complete': False,
}
with Path(__file__).with_name('RESETFIX_GENERATION_EVIDENCE.json').open('x') as stream:
    json.dump(report, stream, indent=2)
print(json.dumps(report, indent=2))
