"""Summarize one frozen campaign, verify saved identities, preserve negative results."""
from analyze import *

def main():
    p=load(HERE/'PREREGISTRATION.json');f=load(HERE/'ALGORITHM_FREEZE.json');s=load(HERE/'SUMMARY.json');execution=load(HERE/'EXECUTION.json')
    assert sha(HERE/'PREREGISTRATION.json')==f['prereg_sha256']
    assert sha(HERE/'input_verified_tracker.py')==f['gate_sha256']==sha(DIAG/'input_verified_tracker.py')
    for rel,h in p['pins'].items():assert sha(PROJECT/rel)==h,rel
    assert load(HERE/'INPUT_GENERATION.json')['time_ns']>f['time_ns']
    assert load(HERE/'PREDICTIONS_FROZEN.json')['time_ns']>load(HERE/'INPUT_GENERATION.json')['time_ns']
    input_records=load(HERE/'INPUT_MANIFEST.json');checks=[]
    for c,r,e in zip(p['cases'],input_records,execution['cases']):
        assert c['id']==r['id']==e['id'] and c['steps']==r['decoded_frames']==e['steps']
        for rel,expected in [(f"inputs/{c['id']}.npy",r['input_sha256']),
                (f"truth/{c['id']}.npz",r['truth_sha256']),(f"videos/{c['id']}.mp4",r['video_sha256']),
                (f"runs/{c['id']}/flow.npy",e['flow_sha256'])]:
            assert sha(HERE/rel)==expected;checks.append(dict(path=rel,sha256=expected))
        flow=np.load(HERE/'runs'/c['id']/'flow.npy',mmap_mode='r');state=np.load(HERE/'runs'/c['id']/'states.npy',mmap_mode='r')
        assert flow.shape==(c['steps'],2,721) and state.shape==(c['steps'],45669)
        del flow,state
    oldparams=np.load(PREVIOUS/'EFFECTIVE_MODEL.npz');newparams=np.load(HERE/'EFFECTIVE_MODEL.npz')
    equal={k:bool(np.array_equal(oldparams[k],newparams[k])) for k in oldparams.files};assert all(equal.values())
    assert np.array_equal(np.load(HERE/'INITIAL_STATE.npy'),np.load(PREVIOUS/'INITIAL_STATE.npy'))
    assert execution['network_weights_unchanged'] and execution['decoder_state_unchanged'] and not execution['GPU']
    assert sum(c['steps'] for c in p['cases'])==execution['neural_steps']==17000
    dump('FINAL_AUDIT.json',dict(status='PASS_FROZEN_IDENTITY_AND_SAVED_DATA_AUDIT_NOT_A_FUNCTIONAL_OVERRIDE',
        functional_status=s['status'],gate_byte_identical_to_previous_candidate=True,all_source_pins_unchanged=True,
        prior_source_MANIFEST_sha256=sha(PREVIOUS/'DELIVERY_MANIFEST.json'),prior_diagnosis_MANIFEST_sha256=sha(DIAG/'DELIVERY_MANIFEST.json'),
        freeze_before_generation=True,predictions_frozen_before_scoring=True,all14_inputs_distinct_from_old=True,
        actual_neural_steps=17000,actual_decoder_frames=17000,all14_shapes_correct=True,
        expanded_parameters_and_edge_indices_bitwise_equal=equal,full_initial_state_bitwise_equal=True,
        checks=checks,full_state_SHA_scope='native CPU worker hashed each full saved state after writing; reuse those fresh identities without another3GB read',
        original11_gate_API_tests_reused='unchanged byte-identical candidate; previous focused tests retained',
        new_gpu_operations=0,board_operations=0,post_test_algorithm_changes=0))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    motion=s['motion'];controls=s['controls'];fig,axs=plt.subplots(2,2,figsize=(14,9))
    ax=axs[0,0];x=np.arange(8);hit=[r['primary']['within18px_fraction'] for r in motion];cov=[r['primary']['coverage'] for r in motion]
    ax.bar(x-.18,hit,.36,label='All motion outputs within18px');ax.bar(x+.18,cov,.36,label='Coverage')
    ax.axhline(.8,color='crimson',ls='--',lw=1,label='Unchanged80% location gate');ax.axhline(.9,color='gray',ls=':',lw=1,label='Unchanged90% coverage')
    ax.set_xticks(x,[r['id'] for r in motion],rotation=35,ha='right',fontsize=7);ax.set_ylim(0,1.14)
    ax.set_title('All8 frozen motion conditions (median gate also applied)');ax.legend(fontsize=7)
    ax=axs[0,1];x=np.arange(6);vals=[r['fraction'] for r in controls];bars=ax.bar(x,vals,color=['steelblue' if r['pass_gate'] else 'crimson' for r in controls])
    ax.axhline(.05,color='black',ls='--',label='Unchanged5% static false-output gate')
    for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.015,f'{v:.1%}',ha='center',fontsize=8)
    ax.set_xticks(x,[r['id'] for r in controls],rotation=30,ha='right',fontsize=8);ax.set_ylim(0,max(.25,max(vals)+.15));ax.set_title('Static object / blank:1s onward');ax.legend(fontsize=7)
    ax=axs[1,0];x=np.arange(8)
    ax.bar(x-.18,[r['without_veto_stop']['late_fraction'] for r in motion],.36,label='Same original flow-only tracker')
    ax.bar(x+.18,[r['stop']['late_fraction'] for r in motion],.36,label='Frozen input-stillness gate')
    ax.set_xticks(x,[r['id'] for r in motion],rotation=35,ha='right',fontsize=7);ax.set_ylim(0,1.05)
    ax.set_title('Motion outputs after stop+0.2s (descriptive, no new cutoff)');ax.legend(fontsize=7)
    ax=axs[1,1];x=np.arange(6)
    ax.bar(x-.18,[r['without_veto_startup_triggers']/r['startup_outputs'] for r in controls],.36,label='Without veto')
    ax.bar(x+.18,[r['startup_triggers']/r['startup_outputs'] for r in controls],.36,label='Frozen gate (first100ms unknown)')
    ax.set_xticks(x,[r['id'] for r in controls],rotation=30,ha='right',fontsize=8);ax.set_ylim(0,1.05)
    ax.set_title('Static scene first1s; all outputs retained');ax.legend(fontsize=7)
    fig.suptitle(f"{s['status']}\nOriginal full FlyVis CPU; algorithm/calibration/gates frozen before14 new videos; no tuning",fontsize=12)
    fig.tight_layout();fig.savefig(HERE/'validation_summary.png',dpi=150);plt.close(fig)
    fig,axs=plt.subplots(2,4,figsize=(15,8))
    for ax,r in zip(axs.flat,motion):
        c=next(c for c in p['cases'] if c['id']==r['id']);truth=np.load(HERE/'truth'/(c['id']+'.npz'))['position'];pred=np.load(HERE/'predictions'/(c['id']+'.npy'));t=pred[:,0]*.005
        active=(t>=c['onset'])&(t<c['stop']);valid=pred[:,1]>0
        ax.plot(truth[:,0],truth[:,1],color='black',lw=2,label='True path')
        ax.scatter(pred[valid&active,2],pred[valid&active,3],s=8,color='crimson',label='Motion-window predictions')
        ax.scatter(pred[valid&~active,2],pred[valid&~active,3],s=5,color='orange',alpha=.5,label='Out-of-motion emissions')
        ax.set(xlim=(-11,11),ylim=(-11,11),title=f"{r['id']}\nwithin18px={r['primary']['within18px_fraction']:.1%}; PASS={r['primary']['pass_gate']}")
        ax.set_aspect('equal');ax.legend(fontsize=5)
    fig.suptitle('All8 new trajectories, including pre-motion/stop emissions; no selected best-case display');fig.tight_layout();fig.savefig(HERE/'all_trajectories.png',dpi=140);plt.close(fig)
    fig,axs=plt.subplots(2,3,figsize=(13,6.5))
    for ax,r in zip(axs.flat,controls):
        pred=np.load(HERE/'predictions'/(r['id']+'.npy'));old=np.load(HERE/'predictions'/(r['id']+'_without_veto.npy'));t=pred[:,0]*.005
        ax.step(t,old[:,1],where='post',label='Without veto',color='orange',alpha=.8)
        ax.step(t,pred[:,1]*.7,where='post',label='Frozen gate (scaled0.7 for visibility)',color='steelblue')
        ax.plot(t,pred[:,11]*.35,color='gray',lw=.6,label='Sensor-change gate open (scaled0.35)')
        ax.scatter(t[pred[:,12]==0],np.full(int((pred[:,12]==0).sum()),-.1),s=10,color='purple',label='UNKNOWN')
        ax.axvline(1,color='black',ls=':',lw=1);ax.set(xlim=(0,5),ylim=(-.2,1.2),title=r['id'],xlabel='Consumed input time(s)');ax.legend(fontsize=5)
    fig.suptitle('All stationary scenes: nuisance variation is not exempted as object motion');fig.tight_layout();fig.savefig(HERE/'control_timelines.png',dpi=150);plt.close(fig)
    # Report exact positive and negative conditions; no result-based test selection.
    lines=['# 冻结静止门控：全新启动、停止、慢速与干扰视频验证','',
        f"2026-10-18。正式功能结果：**{s['status']}**。8个运动条件通过{s['motion_passes']}/8，6个静止/空白条件通过{s['control_passes']}/6。身份审计PASS不覆盖功能失败。",'',
        '## 冻结与真实执行','',
        f"门控代码SHA `{f['gate_sha256']}`，与上一轮候选逐字节相同；预注册SHA `{f['prereg_sha256']}`。先冻结代码/标定/模型/指标，再生成全部14段新MP4；实际721点输入均不同于旧16份记录。全部正常预测保存后再读真值评分。没有重训、调参、排除失败或第二轮神经计算。",'',
        f"原完整FlyVis45,669节点/1,513,231连接，连续Euler、FP32、dt5ms，官方原DecoderGAVP递归eval；模型checkpoint SHA d0e42857e738d0315897c2d50fde9eb3fb1a3fb1f071d55dfc13d53d72bccc3f。17,000个神经步和17,000个官方解码帧真实CPU执行一次，执行段{execution['wall_s']:.3f}s（含输出保存，不含全部准备/导入），CUDA未初始化。展开参数/原边/45,669完整初态与上一轮逐位一致。",'',
        '## 条件与不变门槛','',
        '视频224×224、200fps，5–10.5秒；原721点3×3灰度均值、6px/邻距、黑圆点半径12px与白背景标定不变。运动包括35/125/205/295/55/145/235/325度，速度1/1.5/2/4/5/6邻距每秒，起动0.075–1.65秒，所有运动中途反向。位置为预注册偏心新位置。',
        '噪声是编码前逐帧独立高斯像素sigma2/255，亮度是0.35Hz缓慢全局变暗、最大2%；均先施加再编码/解码。actual decoded variability在INPUT_MANIFEST.json，不能把编码前名义噪声当摄像头噪声标定。',
        '原运动门槛：每条件覆盖≥90%、所有运动评分时刻18px内≥80%、有效中位误差≤12px；所有8条件都须通过。原静止门槛：每条件1秒后误触发≤5%，全部6条件适用，噪声/亮度没有豁免。原空间打乱及固定原点优势各≥20百分点。启动0..1秒和停止+.2秒仍为描述性读出，未偷偷新增或降低验收阈值。',
        '慢速的部分位移接近18px容差，因此另报告“始终保持目标初始位置”的描述性对照；即使主门槛通过，也不自动等于精确速度或方向跟踪。','',
        '## 全部运动条件','']
    for r in motion:
        m=r['primary'];z=r['stop'];lines.append(f"- {r['id']}：覆盖{m['valid']}/{m['n']}={m['coverage']:.2%}，18px内{m['within18px']}/{m['n']}={m['within18px_fraction']:.2%}，中位误差{m['median_valid_px']}px，PASS={m['pass_gate']}。停止+.2s仍触发{z['late_triggers']}/{z['late_outputs']}={z['late_fraction']:.2%}；该段输入门控开放{r['stopped_input_change_fraction']:.2%}；固定初始目标位置对照{r['fixed_initial_target_position_fraction']:.2%}。")
    n=s['counts'];lines+=['',f"合并运动：有效{n['valid']}/{n['primary_outputs']}={s['pooled_coverage']:.2%}，18px内{n['within18px']}/{n['primary_outputs']}={s['pooled_within18px']:.2%}，有效MAE{s['pooled_valid_MAE_px']}px。条件平均命中{s['mean_per_condition_within18px']:.2%}，空间打乱{s['mean_null']:.2%}，固定原点{s['mean_fixed_origin']:.2%}；合并比例与条件平均不混用。",'', '## 全部静止与空白对照','']
    for r in controls:lines.append(f"- {r['id']}：1秒后{r['triggers']}/{r['scored_outputs']}={r['fraction']:.2%}，PASS={r['pass_gate']}；首秒{r['startup_triggers']}/{r['startup_outputs']}（原无门控{r['without_veto_startup_triggers']}次），初期UNKNOWN={r['unknown_outputs']}次；1秒后采样变化门控开放{r['post1s_input_change_fraction']:.2%}。")
    lines+=['', '## 启动/停止、失败与结论边界','',
        f"合并停止+.2秒段：冻结门控{n['late_stop_triggers']}/{n['late_stop_outputs']}次，原无门控{n['without_veto_late_stop_triggers']}次。原始流和神经活动全部保留。首次持续静止时间与右删失标记逐条件在SUMMARY.json；时间以消费input[k]的k×5ms计，输出可用时间再加5ms。", 
        '门控要求过去100ms的721点采样不再变化，首100ms历史不足标UNKNOWN。噪声或亮度变化即便没有目标移动，也可能使它持续开放；之后仍依赖原光流置信度判断。这是该候选需要检验的限制，不能将任何亮度变化定义成目标运动来回避误报。',
        '所有主窗口漏检和超18px位置误差，以及静止场景全部触发（包含评分窗外）在FAILURES.json逐条保存。若噪声/亮度条件失败，保持原结果，不把该视频转训练后仍称留出，也不提高epsilon或原运动阈值。',
        '即使部分条件通过，本研究也只支持受控输入、相同初态、固定白背景标定下的局部定位；未验证自然视频、自动曝光、持续背景运动、多目标、遮挡或物体身份。模型生理真实性和实时/FPGA效果不能由本批推出。','',
        '![全条件指标](validation_summary.png)','', '![全部轨迹](all_trajectories.png)','', '![静止时间轴](control_timelines.png)','',
        '## 复现与收尾','',
        'prepare.py先冻结后生成；run_cpu.py复用已验收原生CPU入口，仅7处字面改动支持变长片段、资源余量与300秒计算上限（RUNNER_ADAPTATION.json）；analyze.py先预测后评分；finish.py核身份并汇总。原API11项定向检查因代码逐字节不变直接复用，未重跑旧大规模验收。',
        '实际命令与日志见reproduce.txt、PREPARE.log、RUN.log、ANALYSIS.log、FINISH.log。该目录使用排他创建，不在封存目录重跑。全部结论按实际CPU执行/软件验证标注；GPU/板/RTL/GUI操作为0。',
        '本轮到此停止；结果出来后不继续调门控或追加新实验。是否需要另立抗干扰改进，应由用户根据全部正负结果决定。']
    with (HERE/'REPORT.md').open('x',encoding='utf-8') as out:out.write('\n'.join(lines)+'\n')
    print(json.dumps(dict(status=s['status'],motion_passes=s['motion_passes'],control_passes=s['control_passes'],counts=n,audit='PASS_IDENTITY_ONLY'),indent=2))

if __name__=='__main__':main()
