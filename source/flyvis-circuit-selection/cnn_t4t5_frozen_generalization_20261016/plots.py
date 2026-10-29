"""Static scientific plots of saved data; no inference."""
from core import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

summary = load(HERE/'SUMMARY.json'); cases = load(HERE/'INPUTS.json'); m = ref.mapping()
plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})
short = [r for r in summary['records'] if r['group'] == 'short']
fig, axes = plt.subplots(2, 2, figsize=(13, 8), layout='constrained')
for ax, key, title, threshold in zip(axes.flat, ['H', 'E', 'M', 'angle'],
    ['H response relative L2', 'Official flow relative error E', 'Flow magnitude ratio M', 'Field angle vs Full (degrees)'], [.2, .2, None, 15]):
    values = []
    for r in short:
        v = r['windows'].get('allpost', {}); f = v.get('flow', {})
        values.append(v.get('H_response_relative_L2') if key == 'H' else f.get({'E':'field_error_E', 'M':'magnitude_ratio', 'angle':'angle_deg'}[key]))
    heights = [np.nan if v is None else v for v in values]
    ax.bar(np.arange(len(short)), heights, color=['#287f79' if r['pass_gate'] else '#ba4a3a' for r in short])
    if threshold is not None: ax.axhline(threshold, color='#ba4a3a', linestyle='--')
    else:
        ax.axhline(.8, color='#ba4a3a', linestyle='--'); ax.axhline(1.2, color='#ba4a3a', linestyle='--')
    ax.set_xticks(np.arange(len(short)), [r['case'] for r in short], rotation=65, ha='right', fontsize=8)
    ax.set_title(title); ax.grid(axis='y', alpha=.15)
fig.suptitle('Frozen 31,168-parameter CNN | fresh short conditions | allpost window')
fig.savefig(HERE/'short_generalization.png', dpi=170); plt.close(fig)

long = [c for c in cases if c['group'] == 'long']; gray = next(c for c in cases if c['group'] == 'gray')
fig, axes = plt.subplots(3, 2, figsize=(13, 9), layout='constrained')
for column, case in enumerate(long):
    z = np.load(HERE/'runs'/case['id']/'STEP_ERRORS.npy'); t = (np.arange(len(z))+1)*DT
    for row, index, title in [(0, 0, 'H state RMSE'), (1, 1, 'R state RMSE'), (2, 6, 'Official flow component RMSE')]:
        ax = axes[row, column]; ax.plot(t, z[:, index], color='#237b83')
        for a, b in [(3, 4), (6, 7), (9, 10)]: ax.axvspan(a, b, color='#a7b5bb', alpha=.2)
        ax.set_title(case['id']+' | '+title); ax.set_xlabel('Model seconds'); ax.grid(alpha=.15)
fig.suptitle('Continuous 10-second closed loops | shaded: stationary grating holds | no reset')
fig.savefig(HERE/'long_closed_loop_errors.png', dpi=170); plt.close(fig)

central = np.load(HERE/'CENTRAL_ACTIVITY.npz'); case = long[0]
fig, axes = plt.subplots(4, 2, figsize=(13, 10), layout='constrained', sharex=True)
for i, ax in enumerate(axes.flat):
    for mode, color in [('Full', '#34495e'), ('CNN', '#d1742a')]:
        activity = central[case['id']+'_'+mode]; t = (np.arange(len(activity))+1)*DT
        ax.plot(t, activity[:, i].mean(1), color=color, label=mode, linewidth=1.15)
    for a, b in [(3, 4), (6, 7), (9, 10)]: ax.axvspan(a, b, color='#a7b5bb', alpha=.16)
    ax.set_title(TYPES[i]); ax.set_ylabel('Original activity units'); ax.set_xlabel('Model seconds'); ax.grid(alpha=.15)
axes[0, 0].legend()
fig.suptitle('GRATING120 | original eight T4/T5 types | mean of fixed central seven positions')
fig.savefig(HERE/'long_T4T5_activity.png', dpi=170); plt.close(fig)

uv = m['grid_uv']; x = np.sqrt(3)/2*uv[1]; y = -(uv[0]+uv[1]/2)
fig, axes = plt.subplots(2, 2, figsize=(11, 9), layout='constrained')
case = long[0]
for row, k in enumerate([500, 1000]):
    arrays = [np.load(HERE/'runs'/case['id']/mode/'flow.npy') for mode in ['Full', 'CNN']]
    if min(len(z) for z in arrays) <= k:
        for ax in axes[row]:
            ax.text(.5, .5, 'INCOMPLETE: requested state not committed', transform=ax.transAxes, ha='center')
            ax.set_axis_off()
        continue
    fields = [z[k] for z in arrays]
    vmax = max(float(np.linalg.norm(z, axis=0).max()) for z in fields)
    for ax, field, mode in zip(axes[row], fields, ['Full', 'CNN']):
        mag = np.linalg.norm(field, axis=0); unit = field/np.maximum(mag, 1e-12)
        scatter = ax.scatter(x, y, c=mag, cmap='viridis', vmin=0, vmax=vmax, s=23)
        select = np.arange(0, 721, 3)
        ax.quiver(x[select], y[select], unit[0, select], unit[1, select], color='white', scale=35, width=.003)
        ax.set_aspect('equal'); ax.set_title(f'{mode} | state t={(k+1)*DT:.3f}s'); ax.set_xlabel('Retinal spacing'); ax.set_ylabel('Retinal spacing')
    fig.colorbar(scatter, ax=axes[row].tolist(), label='Original decoder magnitude; same scale within row')
fig.suptitle('Frozen CNN vs original official optical flow | arrows: unit directions')
fig.savefig(HERE/'long_official_flow.png', dpi=170); plt.close(fig)

fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout='constrained')
selected = [next(c for c in cases if c['id'] == 'ON120_local_upper'), next(c for c in cases if c['id'] == 'OFF120_local_lower'), long[0]]
for ax, case in zip(axes, selected):
    frame = np.load(case['path'])[260]
    ax.scatter(x, y, c=frame, vmin=0, vmax=1, cmap='gray', s=25); ax.set_aspect('equal'); ax.set_title(case['id']+' | input t=1.300s')
fig.savefig(HERE/'actual_retinal_inputs.png', dpi=170); plt.close(fig)
print('SAVED_5_SCIENTIFIC_PLOTS_NO_INFERENCE')
