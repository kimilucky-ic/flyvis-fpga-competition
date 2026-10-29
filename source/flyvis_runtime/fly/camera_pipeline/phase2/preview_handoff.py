"""Read-only local preview of real pixels, 721 input and saved original activity."""
from __future__ import annotations
import argparse
from pathlib import Path
import os
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from camera_pipeline.common import ROOT, sha256, write_json
from camera_pipeline.phase2.gui_handoff import load_experiment, TARGETS


def render(descriptor, destination, step=600):
    os.environ.update(MPLBACKEND='Agg', MPLCONFIGDIR=str(ROOT/'runtime/matplotlib'))
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib.patches import Rectangle
    experiment = load_experiment(descriptor)
    payload = experiment.read_step(step)
    fig = plt.figure(figsize=(13, 8))
    raw_ax = fig.add_subplot(221)
    raw_ax.imshow(payload['bgr'][:, :, ::-1])
    rows = np.array([float(c['source_center_y']) for c in experiment.coordinates])
    cols = np.array([float(c['source_center_x']) for c in experiment.coordinates])
    raw_ax.scatter(cols, rows, s=2, color='lime', alpha=.7)
    raw_ax.add_patch(Rectangle((cols.min()-6, rows.min()-6), cols.max()-cols.min()+12,
                              rows.max()-rows.min()+12, edgecolor='yellow', facecolor='none'))
    raw_ax.set_title(f"Actual source frame {payload['source_frame']} | receipt-relative {payload['source_time_s']:.6f}s")
    raw_ax.axis('off')
    hex_ax = fig.add_subplot(222)
    centers = np.array([[float(c['plot_x']), float(c['plot_y'])] for c in experiment.coordinates])
    angles = np.arange(6)*np.pi/3
    polygon = centers[:, None, :]+np.stack((np.cos(angles), np.sin(angles)), axis=1)[None, :, :]
    collection = PolyCollection(polygon, array=payload['hex_input'], cmap='gray', clim=(0, 1), linewidth=.2)
    hex_ax.add_collection(collection); hex_ax.autoscale_view(); hex_ax.set_aspect('equal')
    hex_ax.set_title(f"Same-step official BoxEye input | t={payload['input_time_s']:.3f}s")
    hex_ax.axis('off'); fig.colorbar(collection, ax=hex_ax, fraction=.035)
    activity_ax = fig.add_subplot(212)
    for cell in TARGETS:
        activity_ax.plot(experiment.activity_time, experiment.activity[0, :, experiment.cell_types.index(cell)],
                         label=cell, linewidth=.8)
    activity_ax.axvline(payload['activity_time_s'], color='black', ls='--', lw=1)
    activity_ax.set_xlabel('Post-Euler-update model time (s)')
    activity_ax.set_ylabel('Actual central T4/T5 activity (model units)')
    activity_ax.legend(ncol=8); activity_ax.grid(alpha=.2)
    fig.suptitle(f"Verified ordinary real scene / offline replay / step {step}\n"
                 f"Source {payload['source_time_s']:.6f}s -> input {payload['input_time_s']:.3f}s -> activity {payload['activity_time_s']:.3f}s")
    fig.tight_layout()
    destination = Path(destination)
    if destination.exists(): raise FileExistsError(destination)
    fig.savefig(destination, dpi=140); plt.close(fig)
    write_json(destination.with_suffix('.json'), {'status': 'PASS', 'kind': 'local_read_only_preview',
               'descriptor_sha256': sha256(descriptor), 'image_sha256': sha256(destination),
               'step': step, 'source_frame': payload['source_frame'], 'source_time_s': payload['source_time_s'],
               'input_time_s': payload['input_time_s'], 'activity_time_s': payload['activity_time_s'],
               'pixel_source': str(experiment.paths['source_frames']), 'activity_source': str(experiment.paths['activity']),
               'controlled_motion': False, 'GUI_loaded': False})
    print(destination)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('descriptor', type=Path); p.add_argument('destination', type=Path)
    p.add_argument('--step', type=int, default=600); a = p.parse_args()
    render(a.descriptor, a.destination, a.step)
