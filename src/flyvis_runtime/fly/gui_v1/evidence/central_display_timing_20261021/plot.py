from pathlib import Path
import os,json,numpy as np
E=Path(r'C:/Users/hzy72/Documents/ChatGPT/fly/gui_v1/evidence/central_display_timing_20261021');os.environ['MPLCONFIGDIR']=str(E/'mpl_cache');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['Microsoft YaHei'];plt.rcParams['axes.unicode_minus']=False;plt.style.use('dark_background');j=json.loads((E/'TIMING.json').read_text());a=np.array(j['central_values']);t=(np.arange(485)+1)*.005;v=np.maximum(a[:,5],0)
fig,ax=plt.subplots(3,1,figsize=(10,7),sharex=True);ax[0].plot(np.arange(485)*.005,j['central_input'],color='#c8dde0');ax[0].set_ylabel('中央感光输入');ax[0].set_title('这次向右暗边缘：中央位置变暗后，T5b短暂响应；并非整段运动一直亮')
ax[1].plot(t,a[:,5],label='中央T5b原值（有正负）',color='#a0abb2');ax[1].plot(t,v,label='右侧整流曲线',color='#e1d65c');ax[1].axhline(0,color='#75808a',lw=.6);ax[1].set_ylabel('真实模型状态');ax[1].legend(loc='lower right')
ax[2].plot(t,.25+.75*np.minimum(1,v/3)**.45,label='改前亮度',color='#839caa');ax[2].plot(t,.18+.82*np.minimum(1,v)**.5,label='改后亮度（固定T5刻度）',color='#e1d65c');ax[2].set_ylabel('骨架显示亮度');ax[2].set_xlabel('模型时间（秒；数学步长仍5ms）');ax[2].set_ylim(0,1.05);ax[2].legend()
for row in ax:row.axvspan(303*.005+.005,325*.005+.005,color='#e1d65c',alpha=.10);row.axvline(1.57,color='#85dcd7',alpha=.6);row.grid(alpha=.12)
fig.tight_layout();fig.savefig(E/'CURRENT_T5_TIMING.png',dpi=130)
