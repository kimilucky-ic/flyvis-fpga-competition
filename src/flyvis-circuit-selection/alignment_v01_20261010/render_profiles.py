"""Scientific comparison of the nine static boundary/profile estimates."""
from pathlib import Path
import json
import os
HERE = Path(__file__).resolve().parent
os.environ['MPLBACKEND'] = 'Agg'
os.environ['MPLCONFIGDIR'] = str(HERE / 'runtime/matplotlib_windows')
import numpy as np
import matplotlib.pyplot as plt

data = json.loads((HERE / 'artifacts/alignment_summary.json').read_text(encoding='utf-8'))['profiles']
names = ['A_T4c', 'B_T5c', 'C_T4T5_all_centers']
labels = ['T4c (92 H nodes)', 'T5c (67 H nodes)', 'Eight T4/T5 centers\n(298 H nodes)']
layouts = ['CURRENT_AGG', 'SOURCE_RAW', 'EDGE_CURRENT']
colors = ['#326496', '#929aa3', '#d5d9dd']
index = {(row['candidate'], row['layout']): row for row in data}
x = np.arange(3)
fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.8), layout='constrained')
for ax, metric, scale, title, ylabel in [
    (axes[0], 'total_payload_bytes_per_step', 1024, 'FP32 payload per logical step', 'Request + response (KiB / step)'),
    (axes[1], 'profile_core_logical_bytes', 1024, 'Logical core and profile-buffer storage', 'Storage (KiB)')]:
    for j, layout in enumerate(layouts):
        raw = np.array([index[(name, layout)][metric] for name in names])
        bars = ax.bar(x + (j - 1) * .24, raw / scale, width=.23, color=colors[j],
            edgecolor='#4f5963', linewidth=.4, label=layout)
        ax.bar_label(bars, labels=[f'{value:.2f}' for value in raw / scale], padding=3, fontsize=9)
    ax.set(title=title, ylabel=ylabel, xlabel='Candidate partition')
    ax.set_xticks(x, labels, fontsize=10)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', alpha=.18)
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(index[(name, layout)][metric] / scale for name in names for layout in layouts) * 1.23)
axes[0].legend(loc='upper left', frameon=False, fontsize=9)
fig.suptitle('FlyVis v0.1 boundary options: explicit x_H in every request', fontsize=14)
fig.text(.5, -.055,
    'Source: audited original graph / flow/0000/000, 2026-10-10. Each FP32 scalar is 4 bytes; 1 KiB = 1024 bytes.\n'
    'Payload excludes headers and transport. Storage is an illustrative logical model, excluding operators, packing and system shell.\n'
    'All profiles remain proposals. No RTL, synthesis, throughput or board validation.',
    ha='center', va='top', fontsize=10)
path = HERE / 'artifacts/boundary_profiles.png'
fig.savefig(path, dpi=150, bbox_inches='tight')
plt.close(fig)
print('Saved', path)
