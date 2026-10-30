from pathlib import Path
import json

def read_limited(path):
    try:
        with path.open('r', errors='replace') as f:
            return f.read(8192)
    except OSError as exc:
        return 'UNAVAILABLE: ' + str(exc)

report = {'evidence': 'READ_ONLY_OS_DRIVER_STATISTICS', 'hardware_actions': 0}
report['meminfo'] = '\n'.join(
    line for line in read_limited(Path('/proc/meminfo')).splitlines()
    if line.split(':')[0] in ('MemTotal', 'MemAvailable', 'CmaTotal', 'CmaFree')
)
report['driver_files'] = {}
for directory, pattern in (
    ('/sys/class/drm', 'card*/device/memstat'),
    ('/sys/kernel/debug/dri', '*/clients'),
):
    try:
        paths = sorted(Path(directory).glob(pattern))[:8]
        if not paths:
            report['driver_files'][directory + '/' + pattern] = 'NOT_AVAILABLE'
        for path in paths:
            report['driver_files'][str(path)] = read_limited(path)
    except OSError as exc:
        report['driver_files'][directory] = 'UNAVAILABLE: ' + str(exc)
print('LINE11_CMA_READONLY', json.dumps(report, ensure_ascii=False, indent=2))
