"""Inspect selected ZIP source members without executing vendor software."""
import hashlib
import json
from pathlib import Path
import zipfile
HERE = Path(__file__).resolve().parent
ARCHIVE = Path('D:/BaiduNetdiskDownload/正点原子/4_Source_Code/5_PYNQ_Design/ZYNQ_7020_PYNQ.zip')

def main():
    result = dict(evidence='READ_ONLY_VENDOR_SOURCE_INSPECTION', archive=str(ARCHIVE),
                  archive_bytes=ARCHIVE.stat().st_size, members=[], blocks=[], hardware_actions=0, vivado_runs=0)
    with zipfile.ZipFile(ARCHIVE) as z:
        selected = [n for n in z.namelist() if n in (
            'ip_repo/cmos_sensor/component.xml', 'ip_repo/cmos_sensor/src/cmos_capture_data.v',
            '6_ov5640_lcd/notebook/ov5640_lcd.ipynb')
            or n.endswith('/ov5640_lcd.srcs/sources_1/bd/base/base.bd')
            or n.endswith('/ov5640_lcd.srcs/constrs_1/new/base.xdc')]
        if len(selected) != 5:
            raise RuntimeError('vendor archive structure changed: expected five members')
        out = HERE/'vendor_reference'
        out.mkdir(exist_ok=True)
        for name in selected:
            raw = z.read(name)
            result['members'].append(dict(member=name, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
            (out/Path(name).name).write_bytes(raw)
            if name.endswith('base.bd'):
                design = json.loads(raw)['design']
                def walk(node, prefix=''):
                    for key, value in node.get('components', {}).items():
                        path = prefix+'/'+key
                        vlnv = value.get('vlnv', '')
                        if any(x in vlnv.lower() for x in ('vdma','vid_in','cmos','iic','pixel_pack')):
                            result['blocks'].append(dict(path=path, vlnv=vlnv, parameters=value.get('parameters', {})))
                        walk(value, path)
                walk(design)
                result['top_interface_nets'] = design.get('interface_nets', {})
    (HERE/'VENDOR_INSPECTION.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(dict(selected_members=len(selected), blocks=len(result['blocks']), hardware_actions=0)))
if __name__ == '__main__':
    main()
