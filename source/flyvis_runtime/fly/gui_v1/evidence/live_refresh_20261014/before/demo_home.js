/* Navigation only: retain the existing readers, renderers, controls and identities. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const demo = $('demoWorkspace'), research = $('researchWorkspace'), advanced = $('advancedWorkspace');
  const selectors = {
    research: [['scientificSparse', '保留节点数量 · 科研 B'], ['scientificPilot', 'T4 / T5 阻断 · 科研先导'], ['phase3Panel', '固定动画 · Full / Python 对照'], ['jointExperiment', 'GPU–FPGA 联合结果 · 需完整验收包']],
    advanced: [['liveCamera', '持续数字输入 / 摄像头与 GPU'], ['liveExperiment', '固定输入 · 新 GPU 实验'], ['flowPanel', '输入预览与冻结'], ['evidenceWorkbench', '运行证据与四模式'], ['inferencePanel', '旧推理接口状态']]
  };
  document.querySelector('.phase3-panel').id = 'phase3Panel';
  document.querySelector('.flow-panel').id = 'flowPanel';
  document.querySelector('.inference-panel').id = 'inferencePanel';
  // Sparse was nested in Pilot. Move both intact, including all existing listeners.
  for (const [group, entries] of Object.entries(selectors)) {
    const host = group === 'research' ? research : advanced;
    const picker = $(group + 'Picker');
    for (const [id, title] of entries) {
      const option = document.createElement('option'); option.value = id; option.textContent = title; picker.append(option);
      const panel = $(id); panel.classList.add('workspace-panel'); host.append(panel);
    }
    picker.addEventListener('change', () => open(group));
  }
  demo.append(document.querySelector('.controls'));
  const help = document.createElement('p'); help.className = 'demo-hint';
  help.textContent = 'ON 是亮刺激，OFF 是暗刺激。左侧看输入，右侧看响应；拖动时间轴查看任意一帧。预刺激灰屏属于原实验的适应阶段。';
  demo.append(help, document.querySelector('.primary-grid'));
  function disclosure(title, className) {
    const details = document.createElement('details'); details.className = className;
    const summary = document.createElement('summary'); summary.textContent = title; details.append(summary);
    details.addEventListener('toggle', () => requestAnimationFrame(() => window.dispatchEvent(new Event('resize'))));
    return details;
  }
  const options = disclosure('选择细胞 / 导出曲线', 'demo-cell-options');
  const toolbar = document.querySelector('.activity-toolbar'); toolbar.before(options); options.append(toolbar);
  const playback = disclosure('速度 / 循环 / 逐帧', 'demo-play-options');
  const playbackBody = document.createElement('div'); playbackBody.className = 'demo-play-options-body';
  for (const element of [document.querySelector('.speed-label'), document.querySelector('.loop-label'), $('step')]) playbackBody.append(element);
  playback.append(playbackBody); document.querySelector('.transport').append(playback);
  document.querySelector('.input-canvases').before(document.querySelector('.transport'));
  const analysis = disclosure('方向分析、官方 DSI 与运行信息', 'demo-analysis'); analysis.id = 'demoAnalysis';
  analysis.append(document.querySelector('.secondary-grid')); demo.append(analysis);
  const modes = disclosure('Full / Python 等对照模式', 'demo-mode-options'); modes.id = 'demoModes';
  modes.append(document.querySelector('.modes')); demo.append(modes);
  $('demoSource').addEventListener('click', () => $('provenanceButton').click());
  for (const id of ['modeNotice', 'importNotice', 'error', 'loading']) demo.prepend($(id));
  const pages = {demo, research, advanced};
  const headings = {
    demo: ['果蝇视觉网络，怎样感知运动？', '跟着一条移动边缘，看输入怎样变成神经响应。选择场景，再点击播放。', 'OFFLINE REPLAY · 真实结果回放'],
    research: ['科研对照', '选择一项已完成的研究，查看真实差异', 'OFFLINE REPLAY · 按来源核验'],
    advanced: ['实验与设备', '手动发起新实验，查看任务和设备状态', '状态以当前任务证据为准']
  };
  function pauseHiddenReplays() {
    for (const id of ['play', 'spPlay', 'srPlay', 'jointPlay']) {
      const button = $(id);
      if (button && !button.getClientRects().length && button.textContent.includes('暂停')) button.click();
    }
  }
  function open(page, panel, updateHash = true) {
    // Recording requires the actual result canvases to remain visible.
    if ($('jointRecord').disabled && $('jointRecording').textContent.startsWith('录制实际离线帧')) return;
    if (!pages[page]) page = 'demo';
    for (const [name, element] of Object.entries(pages)) element.hidden = name !== page;
    for (const button of document.querySelectorAll('[data-workspace]')) button.setAttribute('aria-pressed', String(button.dataset.workspace === page));
    if (selectors[page]) {
      const picker = $(page + 'Picker');
      if (panel && selectors[page].some(([id]) => id === panel)) picker.value = panel;
      for (const [id] of selectors[page]) $(id).hidden = id !== picker.value;
      panel = picker.value;
    }
    const [title, hint, status] = headings[page];
    $('workspaceTitle').textContent = title; $('workspaceHint').textContent = hint; $('workspaceStatus').textContent = status;
    document.body.dataset.workspace = page;
    pauseHiddenReplays();
    if (updateHash) history.replaceState(null, '', '#' + (panel || page));
    requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
  }
  function fromHash() {
    const id = location.hash.slice(1);
    for (const [page, entries] of Object.entries(selectors)) if (entries.some(([panel]) => panel === id)) return open(page, id, false);
    open(['research', 'advanced'].includes(id) ? id : 'demo', null, false);
  }
  for (const button of document.querySelectorAll('[data-workspace]')) button.addEventListener('click', () => open(button.dataset.workspace));
  window.addEventListener('hashchange', fromHash);
  window.addEventListener('flyvis-phase3-open', () => { open('demo'); modes.open = true; });
  window.addEventListener('flyvis-workbench-open', () => open('advanced', 'evidenceWorkbench'));
  $('flowCameraReference').addEventListener('click', () => open('demo'));
  // Navigation does not start or cancel a real computation. Existing stop controls own it.
  document.querySelector('.intro-note').hidden = true;
  document.body.classList.remove('workspace-pending');
  fromHash();
})();
