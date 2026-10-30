'use strict';
// Added only to the independent handoff copy. Values are actual same-step readouts.
(() => {
  const listeners = new Set();
  function frameSnapshot(frame = state.frame) {
    const d = state.dataset;
    if (!d || !state.activity || !state.stimulus || state.loading) return null;
    const k = Math.max(0, Math.min(d.n_frames - 1, Math.round(frame)));
    const count = d.cell_types.length;
    const media = sourceMedia(d);
    const sourceFrame = media?.input_source_indices[k] ?? null;
    const after = d.activity_time_s?.[k] ?? d.time_s[k];
    return {
      schema: 'flyvis-visualization-frame-v1', dataset_id: d.id,
      sample_id: state.sample.sample_id, condition: {...state.sample.conditions}, step_id: k,
      mode: state.comparison ? state.comparisonMode : 'Full_recorded',
      display_kind: 'offline_replay', source_kind: d.source_kind ?? (d.camera ? 'real_windows_camera' : 'validated_synthetic_stimulus'),
      input_time_s: d.time_s[k], activity_after_time_s: after,
      time_reference: d.time_reference,
      source_frame: sourceFrame, source_time_s: sourceFrame === null ? null : media.source_time_s[sourceFrame],
      source_received_utc: sourceFrame === null ? null : media.received_utc?.[sourceFrame] ?? null,
      stimulus: Array.from(state.stimulus.subarray(k * 721, (k + 1) * 721)),
      input_coordinates: d.coordinates.map(row => ({...row})),
      cell_types: [...d.cell_types], central_neurons: d.neurons.map(row => ({...row})),
      activity: Array.from(state.activity.subarray(k * count, (k + 1) * count)),
      comparison_id: state.comparison?.info.comparison_id ?? null,
      run: state.comparison ? {...state.comparison.info.modes[state.comparisonMode]} : null,
      full_activity: state.comparison ? Array.from(state.comparison.arrays.Full_GPU.subarray(k * count, (k + 1) * count)) : null,
      python_activity: state.comparison ? Array.from(state.comparison.arrays.Python_Replacement.subarray(k * count, (k + 1) * count)) : null,
      full_network_max_abs_error: state.comparison?.info.errors.full.max_abs[k] ?? null,
      original_input_sha256: state.sample.source_input_sha256,
      original_recorded_output_sha256: state.sample.source_output_sha256,
      spatial_semantics: '721 genuine input coordinates; 65 selected center readouts, not a complete network spatial map',
      FPGA_available: false
    };
  }
  let previous = '';
  let previousActivity = null;
  function tick() {
    const key = `${state.dataset?.id}/${state.sample?.sample_id}/${state.frame}/${state.comparisonMode}/${state.loading}`;
    if (listeners.size && (key !== previous || previousActivity !== state.activity)) {
      previous = key; previousActivity = state.activity;
      const frame = frameSnapshot();
      if (frame) listeners.forEach(fn => {try {fn(frame);} catch(e) {console.error('3D subscriber failed', e);}});
    }
    requestAnimationFrame(tick);
  }
  window.FlyVisView = Object.freeze({
    getFrame: frameSnapshot,
    seek: step => seek(step),
    pause: () => pause(),
    subscribe: fn => {if(typeof fn !== 'function')throw new TypeError('listener required');listeners.add(fn);previous='';return () => listeners.delete(fn);}
  });
  requestAnimationFrame(tick);
})();
