"""Process-tree concurrency policy and PID-identity-checked owned termination."""
import ntpath
import psutil

EDA = {'vivado.exe', 'xsim.exe', 'xsimk.exe', 'xelab.exe', 'xvlog.exe',
       'xvhdl.exe', 'vitis_hls.exe', 'vitis-run.exe', 'v++.exe', 'rdi_synth.exe'}


def group_eda_records(records):
    by_pid = {r['pid']: r for r in records}
    grouped = {}
    for rec in records:
        if rec['name'].lower() not in EDA:
            continue
        root = rec
        cursor = rec
        visited = {rec['pid']}
        while cursor.get('ppid') in by_pid:
            parent = by_pid[cursor['ppid']]
            if parent['pid'] in visited:
                raise ValueError('Process ancestry cycle')
            visited.add(parent['pid'])
            # A later-created parent PID is a reused PID, not an ancestor.
            if parent['created'] > cursor['created']:
                break
            if parent['name'].lower() in EDA:
                root = parent
            cursor = parent
        group = grouped.setdefault(root['pid'], dict(root=root, members=[]))
        group['members'].append({k: rec[k] for k in ('pid', 'name', 'created')})
    return list(grouped.values())


def collect_eda_snapshot():
    records = []
    errors = []
    for proc in psutil.process_iter(['pid', 'ppid', 'name', 'create_time']):
        try:
            info = proc.info
            if info['name'] is None or info['create_time'] is None:
                errors.append(dict(pid=info['pid'], error='Process identity unavailable'))
                continue
            records.append(dict(pid=info['pid'], ppid=info['ppid'], name=info['name'],
                                created=info['create_time']))
        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied as exc:
            errors.append(dict(pid=proc.pid, error=str(exc)))
    groups = group_eda_records(records)
    live_groups = []
    for group in groups:
        root = group['root']
        try:
            proc = psutil.Process(root['pid'])
            if abs(proc.create_time() - root['created']) > .01:
                errors.append(dict(pid=root['pid'], error='EDA root PID reused during inspection'))
                continue
            root.update(cwd=proc.cwd(), cmdline=proc.cmdline())
            live_groups.append(group)
        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied as exc:
            root['inspection_error'] = str(exc)
            live_groups.append(group)
    return dict(groups=live_groups, inspection_errors=errors)


def isolation_reason(root, own_root):
    if root['name'].lower() != 'vivado.exe':
        return 'EXISTING_INDEPENDENT_NON_VIVADO_EDA'
    cwd = root.get('cwd')
    if root.get('inspection_error') or not cwd or not ntpath.isabs(cwd) or not root.get('cmdline'):
        return 'EXISTING_PROJECT_ISOLATION_UNCONFIRMED'
    own = ntpath.normcase(ntpath.normpath(str(own_root)))
    other = ntpath.normcase(ntpath.normpath(cwd))
    if other == own or other.startswith(own + '\\'):
        return 'EXISTING_JOB_IN_OWN_B_DIRECTORY'
    for arg in root['cmdline']:
        normalized = ntpath.normcase(ntpath.normpath(arg.strip('"')))
        if own in normalized:
            return 'EXISTING_JOB_REFERENCES_OWN_B_DIRECTORY'
    return None


def evaluate_gate(sample, snapshot, allow_concurrent, release_fresh, own_root):
    reasons = []
    if sample['available_MiB'] < 3072:
        reasons.append('AVAILABLE_PHYSICAL_BELOW_3072_MIB')
    if sample['commit_headroom_MiB'] < 4096:
        reasons.append('COMMIT_HEADROOM_BELOW_4096_MIB')
    if snapshot['inspection_errors']:
        reasons.append('PROCESS_INVENTORY_INCOMPLETE')
    groups = snapshot['groups']
    if allow_concurrent:
        if len(groups) > 1:
            reasons.append('TWO_OR_MORE_EXISTING_INDEPENDENT_EDA_JOBS')
        for group in groups:
            reason = isolation_reason(group['root'], own_root)
            if reason:
                reasons.append(reason)
    else:
        if not release_fresh:
            reasons.append('A_RELEASE_NOT_FRESH')
        if groups:
            reasons.append('EXISTING_EDA_JOB_SERIAL_MODE')
    return dict(allowed=not reasons, reasons=reasons, capacity_allowed=
                sample['available_MiB'] >= 3072 and sample['commit_headroom_MiB'] >= 4096,
                allow_concurrent_vivado=allow_concurrent, independent_eda_jobs=len(groups),
                A_release_required=not allow_concurrent)


def terminate_owned(owned, seen, process_factory=psutil.Process):
    """Never use a global process-name kill; recheck PID creation identity."""
    actions = []
    for candidate in reversed(owned):
        try:
            key = (candidate.pid, candidate.create_time())
            if key not in seen:
                continue
            current = process_factory(candidate.pid)
            if abs(current.create_time() - key[1]) > .01:
                actions.append(dict(pid=candidate.pid, action='SKIPPED_REUSED_PID'))
                continue
            current.terminate()
            actions.append(dict(pid=current.pid, created=key[1], action='TERMINATED_OWNED'))
        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied as exc:
            actions.append(dict(pid=candidate.pid, action='TERMINATE_DENIED', error=str(exc)))
    return actions
