"""Verify raw data, independent replay and measured temporal effects; write auditable first-round report."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import csv
import json
import os
import numpy as np
from camera_pipeline.adapter import load_stimulus
from camera_pipeline.common import ROOT,sha256,write_json,utc_now

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def comparison(a,b):
    assert a.shape==b.shape
    difference=a.astype(np.float64)-b.astype(np.float64)
    return {'bitwise_equal':bool(np.array_equal(a,b)),'max_abs_error':float(np.abs(difference).max()),
            'rmse':float(np.sqrt(np.mean(difference*difference))),
            'allclose_atol_rtol_1e5':bool(np.allclose(a,b,atol=1e-5,rtol=1e-5))}

def main():
    os.environ['MPLCONFIGDIR']=str(ROOT/'runtime/matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    results=ROOT/'results'
    report=results/'validation'
    report.mkdir(exist_ok=True)
    paths={name:results/name for name in ('real_camera_native_zoh_r1','real_camera_native_zoh_r2','real_camera_native_linear_r1')}
    bundles={name:load_stimulus(path) for name,path in paths.items()}
    zoh,t,coords,metadata=bundles['real_camera_native_zoh_r1']
    linear=bundles['real_camera_native_linear_r1'][0]
    replay=bundles['real_camera_native_zoh_r2'][0]
    np.testing.assert_array_equal(zoh,replay)
    # Older first-run metadata predates explicit flags; independently rerendered A
    # is exact and records the actual flags. Carry those flags into this lane's metadata.
    explicit_transform=bundles['real_camera_native_zoh_r2'][3]['spatial_transform']
    for name in ('real_camera_native_zoh_r1','real_camera_native_linear_r1'):
        old=bundles[name][3]
        for key in ('mirror_horizontal','mirror_vertical','rotation_degrees','crop','actual_boxeye_internal_resize'):
            old['spatial_transform'][key]=explicit_transform[key]
        old['spatial_transform']['effective_flags_verification']='independent native replay exact; known-direction fixtures passed'
        write_json(paths[name]/'metadata.json',old)
    assert zoh.dtype==np.float32 and zoh.shape==(1,1202,1,721)
    np.testing.assert_array_equal(t,bundles['real_camera_native_linear_r1'][1])
    data_paths={name:results/name for name in ('real_camera_gpu_zoh_r1','real_camera_gpu_zoh_r2','real_camera_gpu_linear_r1','real_camera_cpu_zoh_r1')}
    records={};activities={}
    for name,path in data_paths.items():
        record=read(path/'result.json')
        assert record['status']=='PASS' and record['weights_exact_before'] and record['weights_exact_after']
        for filename,digest in record['data_sha256'].items():
            assert sha256(path/filename)==digest,(name,filename)
        assert record['neurons']==45669 and record['edges']==1513231
        a=np.load(path/'activity_central.npy',allow_pickle=False)
        assert a.shape==(1,1202,65) and np.isfinite(a).all()
        activities[name]=a
        # Add semantic metadata to this lane's earlier outputs; never alter any recorded numerical arrays.
        types=np.load(path/'cell_types.npy',allow_pickle=False)
        nodes=np.load(path/'central_node_indices.npy',allow_pickle=False)
        if not (path/'neurons.csv').exists():
            with (path/'neurons.csv').open('w',newline='',encoding='utf-8') as handle:
                writer=csv.writer(handle);writer.writerow(['cell_type_axis','cell_type','original_node_index','u','v'])
                for index,(cell_type,node) in enumerate(zip(types,nodes)):writer.writerow([index,cell_type,int(node),0,0])
        record.update(job_id=name,activity_axes=['sample','frame','central_cell_type'],
                      activity_spatial_scope='one center neuron (u=v=0) for each of 65 types',
                      target_axes=['sample','frame','central_T4_T5_cell_type'],
                      target_types=[f'T{n}{suffix}' for n in (4,5) for suffix in 'abcd'])
        record['data_sha256']['neurons.csv']=sha256(path/'neurons.csv')
        write_json(path/'result.json',record)
        job=read(path/'gpu_status.json');job.update(job_id=name);write_json(path/'gpu_status.json',job)
        records[name]=record
    recorded=ROOT/'recordings/real_camera_20261010_r1'
    recording=read(recorded/'recording.json')
    capture_job=read(recorded/'job_status.json');capture_job.update(job_id=recorded.name);write_json(recorded/'job_status.json',capture_job)
    frames=np.load(recorded/'frames.npy',allow_pickle=False,mmap_mode='r')
    from camera_pipeline.common import cv2_module
    cv2=cv2_module()
    with (recorded/'frame_timestamps.csv').open(encoding='utf-8') as handle:frame_rows=list(csv.DictReader(handle))
    raw_match=all(np.array_equal(frames[i],cv2.imread(str(recorded/row['path']))) for i,row in enumerate(frame_rows))
    assert raw_match and len(frame_rows)==177
    cap=cv2.VideoCapture(str(recorded/'clip.avi'));decode_count=0
    try:
        while True:
            ok,_=cap.read()
            if not ok:break
            decode_count+=1
    finally:cap.release()
    assert decode_count==177
    g=activities['real_camera_gpu_zoh_r1'];g2=activities['real_camera_gpu_zoh_r2']
    cpu=activities['real_camera_cpu_zoh_r1'];gl=activities['real_camera_gpu_linear_r1']
    gpu_replay=comparison(g,g2);cpu_gpu=comparison(g,cpu)
    assert gpu_replay['bitwise_equal'] and cpu_gpu['allclose_atol_rtol_1e5']
    types=np.load(data_paths['real_camera_gpu_zoh_r1']/'cell_types.npy',allow_pickle=False).astype(str)
    target_indices=[list(types).index(f'T{n}{suffix}') for n in (4,5) for suffix in 'abcd']
    per_type=[]
    for index,cell_type in enumerate(types):
        delta=gl[0,:,index].astype(float)-g[0,:,index].astype(float)
        per_type.append({'cell_type':cell_type,'zoh_linear_max_abs_difference':float(np.abs(delta).max()),
                         'zoh_linear_rmse':float(np.sqrt(np.mean(delta*delta))),
                         'zoh_min':float(g[0,:,index].min()),'zoh_max':float(g[0,:,index].max()),
                         'linear_min':float(gl[0,:,index].min()),'linear_max':float(gl[0,:,index].max())})
    with (report/'temporal_effect_per_cell_type.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(per_type[0]));writer.writeheader();writer.writerows(per_type)
    fig,axes=plt.subplots(2,2,figsize=(12,7),sharex=True)
    for ax,name in zip(axes.flat,['T4a','T4c','T5a','T5c']):
        index=list(types).index(name)
        ax.plot(t+.005,g[0,:,index],label='zero-order hold',linewidth=1)
        ax.plot(t+.005,gl[0,:,index],label='offline linear',linewidth=1,alpha=.8)
        ax.set_title(name);ax.set_ylabel('central model activity (a.u.)');ax.set_xlabel('model post-update time (s)');ax.legend();ax.grid(alpha=.2)
    fig.suptitle('Same real camera clip, identical native BoxEye mapping: temporal policy effect')
    fig.tight_layout();fig.savefig(report/'temporal_effect.png',dpi=150);plt.close(fig)
    with (paths['real_camera_native_zoh_r1']/'time_alignment.csv').open(encoding='utf-8') as handle:zoh_rows=list(csv.DictReader(handle))
    assert all(row['uses_future_frame']=='False' and float(row['source_left_time_s'])<=float(row['model_time_s']) for row in zoh_rows)
    with (paths['real_camera_native_linear_r1']/'time_alignment.csv').open(encoding='utf-8') as handle:linear_rows=list(csv.DictReader(handle))
    acceptance={'status':'PASS','scope':'first-round actual camera capture -> native official BoxEye -> offline full FlyVis CPU/GPU inference',
                'created_utc':utc_now(),'recorded_frame_count':len(frames),'video_decoded_frame_count':decode_count,
                'lossless_png_equals_frames_npy':raw_match,'camera_resolution_wh':[640,480],
                'camera_measured_delivery_fps':recording['measured_delivery_fps'],'source_frame_span_s':recording['recorded_span_s'],
                'stimulus_shape':list(zoh.shape),'dtype':str(zoh.dtype),'stimulus_range':[float(zoh.min()),float(zoh.max())],
                'input_independent_process_replay':comparison(zoh,replay),'GPU_independent_process_replay':gpu_replay,
                'CPU_GPU_fixed_input_activity':cpu_gpu,'unit_checks':read(ROOT/'logs/unit_validation.json'),
                'direction_mapping_checks':read(results/'direction_mapping_validation/result.json'),
                'sampling_region':read(paths['real_camera_native_zoh_r1']/'sampling_region.json'),
                'standard_spatial_policy':'native A','alternative_B_in_neural_comparison':False,
                'zoh_future_input_steps':0,'linear_future_input_steps':sum(row['uses_future_frame']=='True' for row in linear_rows),
                'zoh_linear_input_difference':comparison(zoh,linear),
                'zoh_linear_activity_difference':comparison(g,gl),
                'zoh_linear_T4_T5_difference':comparison(g[:,:,target_indices],gl[:,:,target_indices]),
                'GPU_record':records['real_camera_gpu_zoh_r1'],
                'protected_reference_audit':'logs/protected_after.json',
                'protected_references_unchanged':read(ROOT/'logs/protected_after.json')['protected_hashes_unchanged'],
                'not_accepted':['controlled physical camera motion/brightness conditions','camera angular/physical-speed calibration',
                                'online capture-to-neural-output latency','continuous chunk state preservation','real-time service','optical-flow/object-recognition accuracy']}
    # Policy differences are measured observations, not an allclose acceptance target.
    write_json(report/'acceptance.json',acceptance)
    r=records['real_camera_gpu_zoh_r1']
    text=f'''# 第一轮摄像头视觉输入验收

日期：2026-10-10（Asia/Shanghai）。所有证据均为本机真实 Windows 摄像头采集、官方视觉预处理和原完整 FlyVis 软件推理。

## 已验证

- Windows Integrated Camera，OpenCV 设备 0 / DirectShow。640×480 原图，6 秒录制共 {len(frames)} 帧，首尾实测 {recording['recorded_span_s']:.7f} 秒、交付速率 {recording['measured_delivery_fps']:.5f} FPS。逐帧无损 PNG 与 frames.npy 全部逐位一致；AVI 成功解码 {decode_count} 帧。摄像头已正常释放、重新打开预览，再次释放。编号 15 的不存在设备明确报 CAMERA_UNAVAILABLE。
- 用户确认 A：原始尺寸官方 BoxEye(15,13,mean)，无缩放、裁剪、填边、镜像、旋转。原图与采样区域图见 ../real_camera_native_zoh_r1/camera_receptor_overlay.png。实际使用121641/307200像素，39.5967%；外接范围 x=119..521、y=39..441，外接框角落不等同于实际感受区域。
- Pillow RGB→L 的 float32 /255 沿用官方 sintel_utils.sample_lum。输入六边形顺序同时对照既有 Golden 坐标和本次完整网络所有输入层节点的 u/v，完全一致。
- 已知左右、上下合成边缘：原图方向与采样过渡次序符合预期，反向输入逐位为正向时间反转；直接13×13区域平均与官方输出最大差为0。该测试只验证空间输入映射，不是摄像头运动实验或神经方向调谐。
- 标准刺激 float32 [1,1202,1,721]，值域 [{zoh.min():.9g},{zoh.max():.9g}]；time.npy 为0..6.005秒、dt=.005秒。保留177个实测帧时间、UTC/单调纳秒时钟与1202步来源帧对应关系；独立进程重新预处理逐位一致。
- 原预训练 flow/0000/000，源码 commit {r['source_commit']}；checkpoint SHA256 {r['checkpoint_sha256']}。完整45669节点、1513231边，连续执行整段视频；只在视频之前做一次1秒0.5灰初始化，未逐帧重置。
- 导出中心65类活动 [1,1202,65]、T4/T5中心8类 [1,1202,8]、neurons.csv/cell_types.npy、双时间轴和活动曲线。所有权重/网络缓冲在运行前后精确等于原 checkpoint。独立GPU复算逐位一致、最大误差0；同固定输入CPU/GPU活动最大误差 {cpu_gpu['max_abs_error']:.9g}，RMSE {cpu_gpu['rmse']:.9g}，满足预先沿用GPU Skill的atol=rtol=1e-5。

## 时间和计算

真实摄像头交付FPS≈29.30；模拟输入FPS=200；本次神经计算吞吐 {r['simulation_compute_steps_per_s']:.3f} 步/秒，1202步耗时 {r['inference']['elapsed_s']:.6f} 秒。1秒灰初始化另耗 {r['initialization_timing']['elapsed_s']:.6f} 秒，模型加载 {r['model_load']['elapsed_s']:.6f} 秒。输入转GPU {r['host_to_device']['elapsed_s']*1000:.6f} ms，中心输出回传 {r['device_to_host']['elapsed_s']*1000:.6f} ms。这里的回传只测中心65类，非全45669节点活动传输。

设备 RTX 5060 Laptop，WSL FlyVisCPU，Python3.12.3，torch2.7.1+cu128；CPU复算使用既有torch2.5.1+cpu。CUDA计时均同步。推理相位allocated峰值 {r['inference']['peak_allocated_MiB']:.3f} MiB、reserved峰值 {r['inference']['peak_reserved_MiB']:.3f} MiB；这些数值仅属于本视频和该相位。

主机帧接收时间不是传感器曝光时间。记录出现10个大于1.5倍中位帧间隔的间隙，最大间隔78.527ms；无法据此确认传感器丢帧数。驱动缓冲请求1，但报告-1，实际队列长度未知。视频AVI按常数名义FPS播放，准确时间必须读frame_times.npy/CSV。time.npy标记输入呈现；Euler活动在该输入更新之后，对应activity_time.npy=time.npy+dt。

## 同一真实片段的时间重采样差异

零阶保持真实使用最近已到达帧，未来帧使用数0；离线线性插值使用未来帧的时间步数 {acceptance['linear_future_input_steps']}。空间映射、摄像头数据、权重和初始化保持一致。输入最大差 {acceptance['zoh_linear_input_difference']['max_abs_error']:.9g}；全部中心活动最大差 {acceptance['zoh_linear_activity_difference']['max_abs_error']:.9g}；T4/T5最大差 {acceptance['zoh_linear_T4_T5_difference']['max_abs_error']:.9g}。逐类RMSE/最大差见temporal_effect_per_cell_type.csv；真实曲线见temporal_effect.png。

这些差异说明重采样政策影响数值响应；本段是普通真实场景，不能把差异解释成已校准的方向、速度或光流准确性。线性混合亮度不能恢复摄像头未测得的中间运动。B没有用于神经活动比较。

## 纠错和未验收

最初扫描失败是扫描器按“最后一行”解析多行JSON的脚本错误，不是摄像头不存在。改为解析完整JSON并再次实际扫描后，设备0成功；失败/恢复日志分别保留。独立随机图像13×13均值检查的初始3e-7浮点容差失败，实测最大3.5762787e-7；明确改为1e-6检查卷积与NumPy累加差异，独立方向模式精确平均仍为0差。神经设备对照容差始终沿用1e-5，没有更改模型。

尚未完成受控的真实摄像头静止/左右移动高对比边缘/反向边缘/明暗变化四类采集，没有FOV/物理速度标定，没有连续摄像头GPU状态延续或端到端实时延迟验收。没有运行光流解码器、对象识别、训练或FPGA。摄像头资源释放，工作区其他GUI/实验源码与Golden只读。

可复用的采集器、输入适配和独立重算脚本已保存；重新打开摄像头、固定输入预处理、GPU复算已分别验证。新环境安装和完整端到端二次摄像头录制尚未独立复现，所以本轮不发布新的通用Skill或跨设备兼容性声明。
'''
    (report/'REPORT.md').write_text(text,encoding='utf-8')
    write_json(report/'gui_handoff.json',{'schema':'flyvis-camera-handoff-v1','job_id':'real_camera_gpu_zoh_r1',
               'recording_directory':str(recorded),'input_directory':str(paths['real_camera_native_zoh_r1']),
               'result_directory':str(data_paths['real_camera_gpu_zoh_r1']),'acceptance':'acceptance.json',
               'source_sha256':recording['data_sha256']['frames.npy'],'input_sha256':r['input_sha256'],
               'output_sha256':r['data_sha256']['activity_central.npy'],'activity_axes':r['activity_axes'],
               'cell_identity_files':['cell_types.npy','neurons.csv'],'input_time':'time.npy','activity_time':'activity_time.npy',
               'integration_status':'contract_agreed; GUI has not yet loaded this dataset','execution_kind':'new_inference'})
    write_json(report/'manifest.json',{'created_utc':utc_now(),'files':{str(p.relative_to(ROOT)):sha256(p) for p in ROOT.rglob('*')
               if p.is_file() and p.suffix in ('.py','.ps1','.sh','.md','.npy','.csv','.json','.png','.avi','.log','.txt')
               and not any(part in ('_vendor','runtime','__pycache__') for part in p.relative_to(ROOT).parts)
               and p.name!='manifest.json'}})
    print(json.dumps({'status':'PASS','CPU_GPU':cpu_gpu,'GPU_replay':gpu_replay,
                      'temporal_T4_T5':acceptance['zoh_linear_T4_T5_difference'],'report':str(report/'REPORT.md')}))

if __name__=='__main__':main()
