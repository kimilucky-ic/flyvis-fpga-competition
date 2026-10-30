"""Create a new file-only evidence bundle with the operator's original video.

No PYNQ import or board access. Never changes the original run or recording.
This binds bytes; it does not independently prove that a video is unedited.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import time


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def seal(run, video, output, confirms_unedited):
    run, video, output = run.resolve(), video.resolve(), output.resolve()
    if output == run or run in output.parents:
        raise ValueError('Output must be outside the original run directory')
    if not video.is_file() or video.stat().st_size == 0:
        raise ValueError('Original recording is absent or empty')
    inventory = json.loads((run / 'evidence_manifest.json').read_text(encoding='utf-8'))
    for entry in inventory:
        target = (run / entry['path']).resolve()
        if run not in target.parents or not target.is_file():
            raise ValueError('Run evidence path unresolved/outside run')
        if sha(target) != entry['sha256'] or target.stat().st_size != entry['bytes']:
            raise ValueError('Original run evidence changed: ' + entry['path'])
    report = json.loads((run / 'board_run.json').read_text(encoding='utf-8'))
    request = run / 'request_i32le.bin'
    oracle = run / 'integer_oracle_i32le.bin'
    candidate = run / 'PL_output_i32le.bin'
    if report.get('status') != 'PASS_REAL_BOARD_ONE_STEP_INTEGER_ORACLE' or report.get('python_fallback') is not False:
        raise ValueError('Run is not a successful single-step record; retain failures separately')
    if report.get('committed') is not False or report.get('requested_steps') != 1:
        raise ValueError('Run scope differs from V1 single-step candidate')
    if request.stat().st_size != 1498 * 4 or oracle.stat().st_size != 67 * 4 or candidate.stat().st_size != 67 * 4:
        raise ValueError('Raw word lengths differ from the V1 ABI')
    for path, field in ((request, 'request_sha256'), (oracle, 'integer_oracle_sha256'),
                        (candidate, 'pl_output_sha256')):
        if sha(path) != report[field]:
            raise ValueError('Raw payload hash differs from run record')
    if candidate.read_bytes() != oracle.read_bytes():
        raise ValueError('PL/oracle words differ')
    output.mkdir(parents=True, exist_ok=False)
    shutil.copytree(run, output / 'run')
    recording = output / ('operator_original_video' + video.suffix.lower())
    shutil.copyfile(video, recording)
    if sha(recording) != sha(video):
        raise ValueError('Recording copy identity mismatch')
    comparisons = [{'h_index': index, 'pl_code': actual, 'oracle_code': expected,
                    'exact_match': actual == expected}
                   for index, (actual, expected) in enumerate(zip(
                       struct.unpack('<67i', candidate.read_bytes()),
                       struct.unpack('<67i', oracle.read_bytes())))]
    summary = {'status': 'PASS_FILE_ONLY_EVIDENCE_COPY_AND_67_WORD_COMPARISON',
               'original_run_status': report['status'], 'timestamp_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               'firmware_identity': report['firmware_identity'],
               'request_sha256': sha(request), 'pl_output_sha256': sha(candidate),
               'integer_oracle_sha256': sha(oracle),
               'video': {'source_path': str(video), 'copied_path': recording.name,
                         'bytes': recording.stat().st_size, 'sha256': sha(recording),
                         'operator_confirms_unedited': bool(confirms_unedited),
                         'independent_video_review': 'PENDING'},
               'claim_boundary': 'File-only verification of an operator supplied run and video; not a new live board execution',
               'scientific_acceptance': report.get('scientific_acceptance'),
               'true_closed_loop': False, 'committed': False, 'comparisons': comparisons}
    (output / 'sealed_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    files = [{'path': path.relative_to(output).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)}
             for path in sorted(output.rglob('*')) if path.is_file()]
    (output / 'sealed_manifest.json').write_text(json.dumps(files, indent=2) + '\n', encoding='utf-8')
    print('SEALED_EVIDENCE:', output)
    print('VIDEO_SHA256:', sha(recording))
    print('No board action. Independent recording review remains pending.')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--video', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--operator-confirms-unedited', action='store_true')
    args = parser.parse_args()
    seal(args.run_dir, args.video, args.output_dir, args.operator_confirms_unedited)
