"""Copy the sealed bank-corrected release into a fresh operator delivery ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import time
import zipfile


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    phase = Path(__file__).resolve().parents[1]
    origin = phase / 'build' / 'v1_bankfix_20261011_153525'
    source = phase / 'board_test_20261011' / 'operator_delivery_source'
    target = args.output_dir.resolve()
    target.mkdir(parents=True, exist_ok=False)
    shutil.copytree(origin, target / 'release', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ('board.py', 'seal_video.py', 'README_先读我.md'):
        shutil.copyfile(source / name, target / name)
    (target / 'tools').mkdir()
    shutil.copyfile(phase / 'board_test_20261011/read_only_board_probe.py',
                    target / 'tools/read_only_board_probe.py')
    verifier = (phase / 'board_test_20261011/verify_bankfix_bundle.py').read_text(encoding='utf-8')
    verifier = verifier.replace("parents[1] / 'pynq'", "parents[1] / 'release' / 'pynq'")
    (target / 'tools/verify_sealed_release.py').write_text(verifier, encoding='utf-8')
    # Notebook never starts hardware via Run All: path and confirmation are
    # deliberately empty; run-one must be a separate explicit operator action.
    def cell(kind, lines):
        result = {'cell_type': kind, 'metadata': {}, 'source': lines.splitlines(keepends=True)}
        if kind == 'code':
            result.update({'execution_count': None, 'outputs': []})
        return result
    notebook = {'nbformat': 4, 'nbformat_minor': 5,
                'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}},
                'cells': [
                    cell('markdown', '# FlyVis V1 单步\n先读 README_先读我.md。此 Notebook 只作入口，不含历史板测输出。预检为只读；加载需对确切固件另行确认。\n'),
                    cell('code', '%run board.py preflight\n'),
                    cell('markdown', '把三份预检 JSON 回传核对，按实际事实填写生成的 operator_config.json。下面两个入口单独执行。\n'),
                    cell('code', "PREFLIGHT = ''  # 填终端显示的本次预检目录，核验后才运行\nif not PREFLIGHT:\n    raise ValueError('先填写并复核预检目录')\n%run board.py review --preflight-dir $PREFLIGHT\n"),
                    cell('markdown', 'review 仅记录检查。用户确认确切 BIT/HWH + 加载一次 + row0一次后，开始未剪辑录像，再填写确认文字。若 buffers pinned，保留内核存活，不要重启内核/Run All重试。\n'),
                    cell('code', "CONFIRM = ''  # 确认后手动填 LOAD_REVIEWED_V1_AND_RUN_ROW0_ONCE\nif not PREFLIGHT or CONFIRM != 'LOAD_REVIEWED_V1_AND_RUN_ROW0_ONCE':\n    raise ValueError('未确认确切首次加载和单步；不访问PL')\n%run board.py run-one --preflight-dir $PREFLIGHT --confirm $CONFIRM\n")
                ]}
    for index, item in enumerate(notebook['cells']):
        item['id'] = 'flyvis-v1-{}'.format(index)
    (target / 'FIRST_STEP.ipynb').write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    files = [{'path': path.relative_to(target).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha(path)}
             for path in sorted(target.rglob('*')) if path.is_file()]
    manifest = {'status': 'OPERATOR_PACKAGE_READY; NO_BOARD_EXECUTION',
                'timestamp_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'source_release': str(origin), 'source_release_manifest_sha256': sha(origin / 'release_manifest.json'),
                'board_io_operations_during_packaging': 0,
                'scope': '67-node Q22 first exact overlay load and row0 once; no COMMIT, no replay loop',
                'files': files}
    (target / 'package_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    archive_path = target.with_suffix('.zip')
    with zipfile.ZipFile(archive_path, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(target.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(target.parent).as_posix())
    identity = {'status': 'PACKAGE_CREATED_FILE_ONLY', 'directory': str(target),
                'zip': str(archive_path), 'zip_bytes': archive_path.stat().st_size,
                'zip_sha256': sha(archive_path),
                'package_manifest_sha256': sha(target / 'package_manifest.json'),
                'file_count': len(files), 'board_io_operations': 0}
    with target.with_suffix('.identity.json').open('x', encoding='utf-8') as stream:
        json.dump(identity, stream, indent=2)
        stream.write('\n')
    print(json.dumps(identity, indent=2))


if __name__ == '__main__':
    main()
