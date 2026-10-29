"""Native playback controls around the existing Octarine viewer."""
from pathlib import Path
import argparse, hashlib, json, os, sys, time, traceback
from datetime import datetime, timezone
from scene import ROOT, configure_renderer, research_guard, AnatomyScene
from presentation import describe, verified_identity, NEGATIVE, ZERO, POSITIVE
import numpy as np
import psutil
from PySide6 import QtCore, QtGui, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

def label(text, size=12, color='#aec0d3', bold=False):
    w = QtWidgets.QLabel(text)
    w.setWordWrap(True)
    w.setStyleSheet(f'font-size:{size}px;color:{color};font-weight:{600 if bold else 400};')
    return w

class Player(QtWidgets.QMainWindow):
    def init__(self, args, adapter, run):
        super().init__()
        self.run, self.adapter, self.args = run, adapter, args
        self.is_gpu = adapter['adapter_type'] != 'CPU'
        self.fps_limit = 60 if self.is_gpu else 20
        self.render_times = []
        self.rendered_steps = set()
        self.setWindowTitle('⑩ FlyVis 真实神经元 · 活动回放 · '+('GPU' if self.is_gpu else 'CPU'))
        self.resize(1400,940)
        self.setMinimumSize(1120,800)
        self.setStyleSheet('''QMainWindow,QWidget{background:#091320;color:#e6f1fc;font-family:"Microsoft YaHei UI";font-size:13px;}
            QPushButton{background:#162a3d;border:1px solid #30495c;border-radius:7px;padding:8px 13px;}
            QPushButton:hover{background:#254258;} QPushButton:checked{border:1px solid #5bd8ed;background:#213d50;}
            QSlider::groove:horizontal{height:7px;background:#294152;border-radius:3px;}
            QSlider::sub-page:horizontal{background:#58c7de;border-radius:3px;}
            QSlider::handle:horizontal{width:18px;margin:-6px 0;background:#dbf9fa;border-radius:9px;}
            QComboBox{padding:5px;background:#15283b;border:1px solid #30495c;border-radius:5px;}
            QToolTip{background:#203b52;color:white;border:1px solid #7ea5bc;}''')
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(22,16,22,16)
        root.setSpacing(12)
        header = QtWidgets.QHBoxLayout()
        header.addWidget(label('一个视觉网络，八种神经元类型',24,'#edf6ff',True),1)
        header.addWidget(label('FLYVIS / ON60     ·     本地软件回放',12,'#71c9d9'))
        root.addLayout(header)
        root.addWidget(label('T4a–d 与 T5a–d 同属一个 FlyVis 网络   ·   真实形态：Janelia Optic Lobe v1.1   ·   活动：同类型模型均值',12))
        body = QtWidgets.QHBoxLayout()
        body.setSpacing(18)
        root.addLayout(body,1)
        self.scene = AnatomyScene(args.model,size=(960,700),max_fps=self.fps_limit)
        self.scene.v.canvas.setMinimumSize(600,400)
        left=QtWidgets.QVBoxLayout()
        body.addLayout(left,1)
        filters=QtWidgets.QHBoxLayout()
        self.filter_buttons={}
        for key,title in [('all','全部 8 类'),('T4','T4 群 · 4 类'),('T5','T5 群 · 4 类')]:
            b=QtWidgets.QPushButton(title)
            b.setCheckable(True)
            b.clicked.connect(lambda checked=False,k=key:self.show_group(k))
            filters.addWidget(b)
            self.filter_buttons[key]=b
        self.single=QtWidgets.QCheckBox('只看选中类型')
        self.single.setChecked(False)
        self.single.toggled.connect(lambda enabled:self.apply_filter(self.scene.objects[self.selected]['type'] if enabled else 'all'))
        filters.addWidget(self.single)
        left.addLayout(filters)
        self.observing=label('',15,'#dfeefa',True)
        left.addWidget(self.observing)
        left.addWidget(self.scene.v.canvas,1)
        left.addWidget(label('固定颜色识别类型    ｜    亮度表示活动绝对值    ｜    零活动保留轮廓',12,'#d8e6f2',True))
        gradient=QtWidgets.QFrame()
        gradient.setFixedHeight(13)
        gradient.setStyleSheet('border-radius:5px;background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #58616c,stop:1 #f2f4f8);')
        left.addWidget(gradient)
        ticks=QtWidgets.QHBoxLayout()
        ticks.addWidget(label('0 · 保留 38% 轮廓',11,'#b9c7d7'))
        ticks.addWidget(label('同一全记录固定强度域',11,'#c5d5e5'),1,QtCore.Qt.AlignmentFlag.AlignCenter)
        ticks.addWidget(label(f"|活动| = {self.scene.scale['max']:.3f}",11,'#eff5fa'),0,QtCore.Qt.AlignmentFlag.AlignRight)
        left.addLayout(ticks)
        left.addWidget(label('三维色相固定表示类型；亮度因子依据全程共用 |活动| 范围。原正负数值和零基线见右侧真实曲线。',11))
        side = QtWidgets.QWidget()
        side.setFixedWidth(360)
        sl = QtWidgets.QVBoxLayout(side)
        sl.setContentsMargins(0,0,0,0)
        sl.setSpacing(9)
        body.addWidget(side)
        sl.addWidget(label('类型身份固定，活动数值随时间变化',15,'#e6f1fc',True))
        sl.addWidget(label('点击名称或真实骨架，阅读该类型的活动。',11))
        grid = QtWidgets.QGridLayout()
        self.cards, self.group = [], QtWidgets.QButtonGroup(self)
        self.card_values=[]
        self.group.setExclusive(True)
        for i,o in enumerate(self.scene.objects):
            b = QtWidgets.QPushButton(o['type'])
            b.setCheckable(True)
            b.setMinimumHeight(35)
            b.setFixedWidth(65)
            b.setToolTip(f"真实骨架 body {o['body_id']}；活动来自 {o['count']} 个同类型模型节点的均值")
            b.setStyleSheet(f"border-left:4px solid {self.scene.color_encoding['palette'][o['type']]};")
            self.cards.append(b)
            self.group.addButton(b,i)
            row=QtWidgets.QHBoxLayout()
            row.setSpacing(6)
            row.addWidget(b)
            number=label('',14,'#d7e3ef',True)
            row.addWidget(number,1)
            self.card_values.append(number)
            grid.addLayout(row,i//2,i%2)
        self.group.idClicked.connect(self.select)
        sl.addLayout(grid)
        self.detail = label('',14,'#cdeafa',True)
        self.value = label('',27,'#f7ecd0',True)
        self.mapping = label('',11)
        sl.addWidget(self.detail)
        sl.addWidget(self.value)
        self.explanation=label('',13,'#deebf6')
        self.change=label('',12,'#aacbdf')
        sl.addWidget(self.explanation)
        sl.addWidget(self.change)
        sl.addWidget(self.mapping)
        self.figure = Figure(figsize=(3.14,1.65),dpi=100,facecolor='#091320')
        self.plot = FigureCanvasQTAgg(self.figure)
        self.plot.setFixedHeight(160)
        self.ax = self.figure.add_subplot(111,facecolor='#091320')
        self.figure.subplots_adjust(left=.19,right=.96,bottom=.26,top=.93)
        self.ax.tick_params(colors='#97acc2',labelsize=8)
        self.ax.set_xlabel('活动时间（秒）',fontfamily='Microsoft YaHei',color='#97acc2',fontsize=8)
        self.ax.set_ylabel('模型值',fontfamily='Microsoft YaHei',color='#97acc2',fontsize=8)
        for spine in self.ax.spines.values(): spine.set_color('#2a4054')
        self.ax.grid(alpha=.12,color='#a9bdce')
        self.ax.axhline(0,color='#7c8e9f',linewidth=.8,linestyle='--')
        self.line, = self.ax.plot([],[],color='#62d7e5',linewidth=1.7)
        self.cursor = self.ax.axvline(0,color='#ffe0a2',linewidth=1,animated=True)
        self.dot, = self.ax.plot([],[],'o',color='#ffe0a2',markersize=5,animated=True)
        self.plot_background = None
        self.plot.mpl_connect('draw_event',self.cache_plot)
        sl.addWidget(self.plot)
        sl.addWidget(label('曲线：该类型的真实保存记录；虚线为数值 0。\n所有类型采用相同纵轴范围和颜色标尺。',11,'#94c2cf'))
        sl.addStretch(1)
        sl.addWidget(label('半透明背景：ME / LO / LOP（右侧）\n拖动旋转 · 滚轮缩放 · 线宽仅用于辨识',11))
        controls = QtWidgets.QHBoxLayout()
        self.play = QtWidgets.QPushButton('▶  播放')
        self.play.setFixedWidth(108)
        self.play.clicked.connect(self.toggle)
        controls.addWidget(self.play)
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setRange(0,len(self.scene.time)-1)
        self.slider.setAccessibleName('模型时间步进度')
        self.slider.sliderPressed.connect(self.pause)
        self.slider.valueChanged.connect(self.seek)
        controls.addWidget(self.slider,1)
        self.clock = label('',13,'#d9e9f7',True)
        self.clock.setMinimumWidth(240)
        controls.addWidget(self.clock)
        self.speed = QtWidgets.QComboBox()
        for title,rate in [('细看',4),('演示 · 12步/秒',12),('标准',32),('快速',64)]: self.speed.addItem(title,rate)
        self.speed.setCurrentIndex(1)
        self.speed.currentIndexChanged.connect(self.rebase)
        controls.addWidget(self.speed)
        root.addLayout(controls)
        foot = QtWidgets.QHBoxLayout()
        foot.addWidget(label('整条骨架统一着色：类型级模型映射；非个体生物测量，非 FPGA 实板结果。',12,'#e5c49d'),1)
        for text,fn in [('骨架近景',self.scene.detail_view),('脑区全景',self.scene.overview)]:
            b=QtWidgets.QPushButton(text);b.clicked.connect(fn);foot.addWidget(b)
        root.addLayout(foot)
        self.performance = label(self.device_text()+' · 已暂停',11,'#83b7ca')
        root.addWidget(self.performance)
        self.timer = QtCore.QTimer(self)
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer.setInterval(16 if self.is_gpu else 50)
        self.timer.timeout.connect(self.tick)
        self.scene.v.renderer.add_event_handler(self.on_render,'before_render')
        self.fps_timer = QtCore.QTimer(self)
        self.fps_timer.setInterval(1000)
        self.fps_timer.timeout.connect(self.show_performance)
        self.fps_timer.start()
        self.safety_timer=QtCore.QTimer(self)
        self.safety_timer.setInterval(3000)
        self.safety_timer.timeout.connect(self.memory_check)
        self.safety_timer.start()
        self.selected = 0
        self.scene.v.renderer.add_event_handler(self.pick,'pointer_down')
        self.select(0)
        self.apply_filter('all')
        self.set_frame(0)
        self.record = dict(started_utc=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),adapter=adapter,
                           scientific_boundary=self.scene.model['scientific_boundary'], source='model.json',
                           status='OPEN', free_bytes_start=psutil.virtual_memory().available,
                           rendering='Octarine/pygfx '+args.renderer+' / D3D12; saved data replay only',fps_limit=self.fps_limit,
                           preflight=research_guard())
        self.save_record()

    def save_record(self):
        self.record['rss_bytes']=psutil.Process().memory_info().rss
        (self.run/'run.json').write_text(json.dumps(self.record,ensure_ascii=False,indent=2),encoding='utf-8')

    def log(self,event,**kw):
        with open(self.run/'events.jsonl','a',encoding='utf-8') as f:
            f.write(json.dumps(dict(event=event,time_utc=datetime.now(timezone.utc).isoformat(),**kw),ensure_ascii=False)+'\n')

    def memory_check(self):
        if self.is_gpu:
            guard=research_guard()
            if guard['busy'] or guard['markers']:
                self.record.update(yielded_to_research=guard)
                self.log('yield_to_research',**guard)
                self.close()
                return
        if psutil.virtual_memory().available < 800*1024**2:
            self.pause()
            self.record['memory_pause']=True
            self.save_record()

    def device_text(self):
        return ('GPU · '+self.adapter['device'] if self.is_gpu else 'CPU 软件绘制')

    def on_render(self,event):
        if self.timer.isActive():
            self.render_times.append(time.perf_counter())
            self.rendered_steps.add(self.scene.frame)

    def show_performance(self):
        if self.timer.isActive():
            now=time.perf_counter()
            recent=[t for t in self.render_times if t>=now-2]
            fps=(len(recent)-1)/(recent[-1]-recent[0]) if len(recent)>1 else 0
            self.performance.setText(f'{self.device_text()} · 绘制 {fps:.1f} 帧/秒 · 活动 {self.speed.currentData()} 步/秒')
        else:
            self.performance.setText(self.device_text()+' · 已暂停（停止持续绘制）')

    def save_playback_stats(self):
        times=np.asarray(self.render_times)
        if len(times)<2:return
        intervals=np.diff(times)
        stats=dict(renderer=self.args.renderer,rendered_frames=len(times),elapsed_s=float(times[-1]-times[0]),
                   render_fps=float((len(times)-1)/(times[-1]-times[0])),p95_frame_ms=float(np.percentile(intervals,95)*1000),
                   distinct_saved_steps=len(self.rendered_steps),steps_per_second=self.speed.currentData(),
                   viewport_logical_size=list(self.scene.v.size),pixel_ratio=self.scene.v.renderer.pixel_ratio,
                   measurement='pygfx before_render event, once per rendered scene frame; not physical display scanout',
                   interpolation='none; display refresh may repeat a saved activity sample')
        self.record['last_playback']=stats
        self.log('playback_stats',**stats)
        (self.run/'playback.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
        self.save_record()

    def select(self,i):
        self.selected=int(i)
        self.cards[i].setChecked(True)
        o=self.scene.objects[i]
        self.detail.setText(f"{o['type']}   ·   body {o['body_id']}")
        self.mapping.setText(f"{o['count']} 个同类型模型节点的均值\n单位：模型内部单位（保留正负值）")
        self.line.set_data(self.scene.time,self.scene.activity[:,i])
        self.ax.set_ylim(-self.scene.scale['max']*1.08,self.scene.scale['max']*1.08)
        self.ax.set_xlim(self.scene.time[0],self.scene.time[-1])
        self.plot_background = None
        self.update_detail()
        if self.single.isChecked(): self.apply_filter(o['type'])
        self.log('select',type=o['type'],body_id=o['body_id'])

    def show_group(self,key):
        self.single.blockSignals(True)
        self.single.setChecked(False)
        self.single.blockSignals(False)
        self.apply_filter(key)
        shown=[i for i,o in enumerate(self.scene.objects) if key in ('all',o['type'],o['type'][:2])]
        if self.selected not in shown: self.select(shown[0])

    def apply_filter(self,key):
        self.scene.filter_types(key)
        for k,b in self.filter_buttons.items(): b.setChecked(k==key)
        names=[o['type'] for o in self.scene.objects if key in ('all',o['type'],o['type'][:2])]
        self.observing.setText('正在观察 '+('全部八类' if key=='all' else key+' 群' if key in ('T4','T5') else key)+'    ·    '+str(len(names))+' 条真实重建骨架')
        self.log('type_filter',type_filter=key,visible_types=names)

    def pick(self,event):
        if getattr(event,'button',1)!=1: return
        info=self.scene.v.renderer.get_pick_info((event.x,event.y))
        target=info.get('world_object')
        name=getattr(target,'_object_id',None)
        for i,o in enumerate(self.scene.objects):
            if o['name']==name:
                self.select(i)
                self.log('neuron_pick',type=o['type'],body_id=o['body_id'])
                break
        else:
            self.log('pick_background',x=float(event.x),y=float(event.y))

    def cache_plot(self,event):
        self.plot_background=self.plot.copy_from_bbox(self.ax.bbox)
        self.draw_plot_cursor()

    def draw_plot_cursor(self):
        self.plot.restore_region(self.plot_background)
        self.ax.draw_artist(self.cursor)
        self.ax.draw_artist(self.dot)
        self.plot.blit(self.ax.bbox)

    def update_detail(self):
        f,i=self.scene.frame,self.selected
        self.value.setText(f"{self.scene.activity[f,i]:+.6f}")
        d=describe(self.scene.objects,self.scene.activity,self.scene.time,f,i)
        self.explanation.setText(d['explanation'])
        self.change.setText(d['change'])
        self.mapping.setText(d['mapping']+'\n单位：模型内部单位；骨架 body ID 仅标识形态。')
        self.cursor.set_xdata([self.scene.time[f]]*2)
        self.dot.set_data([self.scene.time[f]],[self.scene.activity[f,i]])
        if self.plot_background is None:self.plot.draw_idle()
        else:self.draw_plot_cursor()

    def set_frame(self,index):
        self.scene.set_frame(index)
        f=self.scene.frame
        self.slider.blockSignals(True);self.slider.setValue(f);self.slider.blockSignals(False)
        self.clock.setText(f"第 {f+1:03d} / {len(self.scene.time)} 步   t = {self.scene.time[f]:+.3f} s")
        for i,(o,c,b) in enumerate(zip(self.scene.objects,self.scene.colors,self.cards)):
            color='#'+''.join(f'{round(x*255):02x}' for x in c)
            b.setText(o['type'])
            self.card_values[i].setText(f"{self.scene.activity[f,i]:+.3f}")
            self.card_values[i].setStyleSheet(f'color:#e1edf7;font-size:14px;font-weight:600;border-bottom:2px solid {color};padding-bottom:3px;')
        self.update_detail()

    def seek(self,index):
        self.set_frame(index)
        self.rebase()
        self.log('seek',frame=index,time_s=float(self.scene.time[index]))

    def rebase(self,*unused):
        self.start_frame=self.scene.frame
        self.started=time.perf_counter()

    def toggle(self):
        if self.timer.isActive(): self.pause()
        else:
            if self.scene.frame==len(self.scene.time)-1: self.set_frame(0)
            self.render_times=[];self.rendered_steps=set()
            self.scene.v.render_trigger='continuous' if self.is_gpu else 'reactive'
            self.rebase();self.timer.start();self.play.setText('Ⅱ  暂停')
            self.log('play',frame=self.scene.frame,steps_per_second=self.speed.currentData())

    def pause(self):
        was_playing=self.timer.isActive()
        self.timer.stop();self.play.setText('▶  播放')
        self.scene.v.render_trigger='reactive'
        if was_playing:self.save_playback_stats()
        self.log('pause',frame=self.scene.frame)

    def tick(self):
        index=self.start_frame+int((time.perf_counter()-self.started)*self.speed.currentData())
        if index!=self.scene.frame:self.set_frame(index)
        if index>=len(self.scene.time)-1: self.pause()

    def closeEvent(self,event):
        if self.timer.isActive():self.pause()
        self.timer.stop();self.safety_timer.stop();self.fps_timer.stop()
        self.record.update(status='CLOSED',last_frame=self.scene.frame)
        self.save_record()
        self.scene.v.close()
        event.accept()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--model',type=Path,default=ROOT/'model.json')
    ap.add_argument('--tag',default=datetime.now().strftime('%Y%m%d_%H%M%S'))
    ap.add_argument('--autoplay',action='store_true')
    ap.add_argument('--renderer',choices=['gpu','cpu'],default='gpu')
    ap.add_argument('--benchmark-seconds',type=float,default=0)
    ap.add_argument('--keep-open',action='store_true')
    args=ap.parse_args()
    run=ROOT/'evidence'/args.tag
    run.mkdir(parents=True,exist_ok=True)
    def offline(event,parameters):
        if event=='socket.connect' and not (isinstance(parameters[1],tuple) and parameters[1][0] in ('127.0.0.1','::1','localhost')):
            raise RuntimeError('Replay uses local files only; external Python network connection denied')
    sys.addaudithook(offline)
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    adapter=configure_renderer(args.renderer)
    app=QtWidgets.QApplication(sys.argv)
    app.setFont(QtGui.QFont('Microsoft YaHei UI',10))
    loading=QtWidgets.QProgressDialog('正在读取本地真实骨架与已保存的活动记录…\n绘制设备：'+adapter['device'],None,0,0)
    loading.setWindowTitle('⑩ 正在打开活动回放')
    loading.setCancelButton(None)
    loading.setMinimumDuration(0)
    loading.resize(480,110)
    loading.show()
    app.processEvents()
    identity=verified_identity(args.model)
    window=Player(args,adapter,run)
    window.record['verified_identity']=identity
    window.save_record()
    window.show()
    loading.close()
    if args.autoplay or args.benchmark_seconds:
        QtCore.QTimer.singleShot(1500,window.toggle)
    if args.benchmark_seconds:
        QtCore.QTimer.singleShot(int(1500+1000*args.benchmark_seconds),window.pause if args.keep_open else window.close)
    return app.exec()

if __name__=='__main__':
    try: sys.exit(main())
    except Exception:
        error=traceback.format_exc()
        (ROOT/'evidence/last_error.log').write_text(error,encoding='utf-8')
        import ctypes
        ctypes.windll.user32.MessageBoxW(None,'回放器未能打开。错误记录：\n'+str(ROOT/'evidence/last_error.log')+'\n\n'+error[-850:],'⑩ 活动回放',0x10)
        raise
