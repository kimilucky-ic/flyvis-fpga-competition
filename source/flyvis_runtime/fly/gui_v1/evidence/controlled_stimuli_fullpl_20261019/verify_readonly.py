"""Independent CPU consumer audit. No inference, decoder, listener or device.

Run once against the explicitly pinned package. Writes only this evidence folder.
"""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from time import perf_counter

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
GUI = HERE.parents[1]
ROOT = GUI.parent.parent/'fpga/flyvis-circuit-selection/controlled_stimuli_20261019_v1'
PACK_SHA = '7291e37f21a94244b81fb916dca0296d310ce354ac32fc4c8e9077d6aeac3500'
MANIFEST_SHA = 'a398175a2f9080d5a1aaa49ceb57ee3fe57dcbe282521e55cc373fa0669302c1'
KEYS = (0, 199, 200, 400, 484)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()


def path(relative):
    p = (ROOT/relative).resolve()
    assert p.is_relative_to(ROOT.resolve()), 'Package path escape'
    return p


def read(relative):
    return json.loads(path(relative).read_text(encoding='utf-8-sig'))


def csv_rows(relative):
    with path(relative).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    began = perf_counter()
    assert sha(path('PACK.json')) == PACK_SHA
    assert sha(path('DELIVERY_MANIFEST.json')) == MANIFEST_SHA
    pack, manifest = read('PACK.json'), read('DELIVERY_MANIFEST.json')
    checked = {}
    for item in manifest['files']:
        p = path(item['path'])
        assert p not in checked and p.stat().st_size == item['bytes']
        checked[p] = sha(p)
        assert checked[p] == item['sha256'], item['path']
    assert len(checked) == 2160 and manifest['PACK_sha256'] == PACK_SHA
    assert read('VALIDATION.json')['status'] == 'PASS_CPU_STIMULUS_AND_INTERFACE_ONLY'
    assert read('RENDER_AUDIT.json')['reference_bitwise_equal'] is True
    assert pack['schema'] == 'flyvis-controlled-stimuli/v1'
    assert pack['model_nodes'] == 45669 and pack['model_edges'] == 1513231
    assert pack['neural_results'] is pack['model_comparison_id'] is None
    assert pack['all_backends_status'] == 'NOT_RUN'
    # Only the SHA-checked optional reader is imported, never generator/runtime.
    module_spec = importlib.util.spec_from_file_location('line4_readonly_frozen_input', path('reader.py'))
    reader = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(reader)
    rows, inputs, mapping = [], {}, {}
    pixels_checked = set()
    for condition in pack['conditions']:
        cid = condition['condition_id']; source = reader.FrozenInput(ROOT, cid)
        assets = condition['paths']
        array = source.input; inputs[cid] = array
        binary = np.fromfile(path(assets['raw_input']['path']), dtype='<f4').reshape(485,721)
        movie = np.load(path(assets['stimulus']['path']), allow_pickle=False, mmap_mode='r')
        assert np.array_equal(array.view('<u4'), binary.view('<u4'))
        assert movie.shape == (1,485,1,721) and np.array_equal(array.view('<u4'), movie[0,:,0].view('<u4'))
        assert hashlib.sha256(array.tobytes()).hexdigest() == condition['input_raw_sha256']
        t = np.load(path(assets['input_time']['path']), allow_pickle=False)
        after = np.load(path(assets['state_time']['path']), allow_pickle=False)
        assert np.array_equal(t, np.arange(485)*.005)
        assert np.array_equal(after, (np.arange(485)+1)*.005)
        timeline = csv_rows(assets['frame_map']['path']); mapping[cid] = timeline
        assert len(timeline) == 485
        for k,row in enumerate(timeline):
            assert int(row['step_id']) == int(row['video_frame']) == k
            assert float(row['input_time_s']) == t[k] and float(row['state_time_s']) == after[k]
            assert float(row['video_pts_s']) == k/50
            p = path(row['source_png']); assert p in checked
            if p not in pixels_checked:
                with Image.open(p) as im:
                    a = np.asarray(im)
                    assert im.mode == 'L' and a.shape == (418,418)
                    assert hashlib.sha256(a.tobytes()).hexdigest() == row['pixel_sha256']
                pixels_checked.add(p)
        for k in KEYS:
            f = source.frame(k)
            assert f['neural_state'] is f['flow'] is None
            assert f['video_frame'] == k and f['video_pts_s'] == k/50
            assert np.array_equal(f['input_721'], array[k])
        assert np.array_equal(array[400:], np.broadcast_to(array[400], (85,721)))
        if condition['stationary']:
            assert np.array_equal(array, np.broadcast_to(array[0], (485,721)))
        assert condition['neural_results'] is condition['comparison_id'] is None
        assert condition['GPU_execution'] is condition['FPGA_execution'] is False
        rows.append(dict(condition_id=cid,stationary=condition['stationary'],
                         input_raw_sha256=condition['input_raw_sha256'],steps=485,
                         key_steps=list(KEYS),neural_state=None,flow=None,status='STIMULUS_ONLY_NOT_RUN'))
    for c in pack['conditions']:
        if c['matched_control']:
            assert np.array_equal(inputs[c['condition_id']][:201], inputs[c['matched_control']][:201])
    declared_complements = {row['direction']: row['max_abs_error'] for row in read('VALIDATION.json')['ON_OFF_complements']}
    complement_errors = {}
    for direction in ('RIGHT','UP','LEFT','DOWN'):
        assert not np.array_equal(inputs['BAR_BRIGHT_'+direction], inputs['BAR_BRIGHT_'+direction+'_STATIC'])
        err = float(np.max(np.abs(inputs['EDGE_ON_'+direction]+inputs['EDGE_OFF_'+direction]-1)))
        # Match the frozen official-BoxEye audit, not exact arithmetic complement.
        assert err == declared_complements[direction] and err < 2e-6
        complement_errors[direction] = err
    assert not np.array_equal(inputs['BAR_BRIGHT_RIGHT'],inputs['BAR_BRIGHT_LEFT'])
    assert not np.array_equal(inputs['DOT_CCW'],inputs['DOT_CW'])
    coordinates = csv_rows(pack['coordinates']['path'])
    uv = [(int(v['u']),int(v['v'])) for v in coordinates]
    assert len(uv) == len(set(uv)) == 721 and uv == sorted(uv)
    ids = np.load(path(pack['T4T5_global_ids']['path']),allow_pickle=False)
    assert ids.shape == (8,721) and len(np.unique(ids)) == 5768
    nodes = csv_rows('nodes_full.csv')
    for j,typ in enumerate(pack['T4T5_global_ids']['types']):
        for index,node_id in enumerate(ids[j]):
            node=nodes[int(node_id)]
            assert int(node['global_node_index'])==node_id and node['cell_type']==typ
            assert (int(node['u']),int(node['v']))==uv[index]
    initials = {}
    for name,item in pack['initial_state_assets'].items():
        p=path(item['path']); a=np.load(p,allow_pickle=False)
        assert a.dtype==np.dtype('<f4') and a.shape==(45669,) and np.isfinite(a).all()
        assert sha(p)==item['file_sha256']
        assert hashlib.sha256(a.tobytes()).hexdigest()==item['raw_array_sha256']
        initials[name]=dict(file_sha256=item['file_sha256'],raw_array_sha256=item['raw_array_sha256'])
    old_plan=json.loads((GUI/'evidence/line11_ddr485_on60_20261018/plan/RUN_PLAN.json').read_text())
    assert initials['original_bias_fp32']['raw_array_sha256']==old_plan['initial_state']['sha256']
    assert initials['original_bias_fp32']['raw_array_sha256']!=initials['gray_adapted_fp32']['raw_array_sha256']
    for bad in (-1,485,True,1.5):
        try: source.frame(bad)
        except ValueError: pass
        else: raise AssertionError('Invalid frame accepted')
    assert not {'torch','cv2','pynq'}.intersection(sys.modules)
    # This sheet is an actual data preview, explicitly not a GUI screenshot/result.
    ids_to_show=('BAR_BRIGHT_RIGHT','EDGE_ON_RIGHT','EDGE_OFF_RIGHT','DOT_CCW')
    image=Image.new('RGB',(1920,1080),'#09131f'); draw=ImageDraw.Draw(image)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',24)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    draw.text((28,18),'纯FPGA接口 · 冻结科学刺激CPU读取预览（非GUI截图）',font=font,fill='#b4f0e3')
    draw.text((28,58),'28条件已读；神经活动 / 官方光流 / 功能评价：待计算 NOT_RUN；未生成RUN_PLAN或板端授权',font=small,fill='#f5c276')
    for y,cid in enumerate(ids_to_show):
        draw.text((28,106+y*237),cid,font=small,fill='#b5d8e5')
        for x,k in enumerate(KEYS):
            with Image.open(path(mapping[cid][k]['source_png'])) as im:
                image.paste(im.convert('RGB').resize((188,188)),(240+x*324,100+y*237))
            draw.text((240+x*324,291+y*237),f'k={k} / 模型{k*.005:.3f}s / 视频{k/50:.2f}s',font=small,fill='#c4d3df')
    preview=HERE/'CPU_INPUT_PREVIEW.png'; image.save(preview)
    result=dict(status='PASS_READONLY_CPU_INPUT_CONSUMPTION_NO_NEURAL_RESULT',
                pack_sha256=PACK_SHA,manifest_sha256=MANIFEST_SHA,
                files_checked=len(checked),bytes_checked=manifest['total_bytes'],
                conditions=rows,model_input_rows_checked=28*485,
                unique_source_pixels_checked=len(pixels_checked),
                initial_assets=initials,current_bias_identity_matches=True,
                ON_OFF_complement_errors= complement_errors,
                model_dt_s=.005,model_duration_s=2.425,preview_fps=50,preview_duration_s=9.7,
                preview_png=str(preview),preview_sha256=sha(preview),
                model_steps_executed=0,decoder_calls=0,device_operations=0,GUI_launched=False,
                source_reader_sha256=checked[path('reader.py')],
                pending=['Actual new initial/profile/comparison binding','Paired numerical reference and states',
                         'Actual purePL run','Actual official flow','Browser/native visual verification'],
                elapsed_s=perf_counter()-began)
    (HERE/'READONLY_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(result['status'],len(rows),'conditions',len(checked),'files',len(pixels_checked),'pixel frames',round(result['elapsed_s'],3),'s')


if __name__=='__main__':main()
