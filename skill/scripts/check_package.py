"""Offline document/integrity checks only; never opens a board, GPU or EDA tool.

Run: python scripts/check_package.py
Optionally pass --output /path/to/result.json (an explicit output location).
No third-party dependency. Historical result status is never treated as a new run.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from urllib.parse import unquote


def audit(root):
    errors = []
    links = 0
    index = json.loads((root / 'audit_index.json').read_text(encoding='utf-8'))
    manifest = json.loads((root / 'evidence/source_manifest.json').read_text(encoding='utf-8'))
    if len(index) != 14 or len({x['name'] for x in index}) != 14:
        errors.append('Expected exactly fourteen unique inventoried Skills')
    for p in root.rglob('*'):
        if p.name != 'README.md' and not re.fullmatch(r'[a-z0-9_-]+(?:\.[a-z0-9_-]+)*', p.name):
            errors.append('Nonconforming submitted name: ' + str(p.relative_to(root)))
        if not p.is_file():
            continue
        if p.suffix == '.json':
            try:
                json.loads(p.read_text(encoding='utf-8-sig'))
            except (ValueError, UnicodeError) as e:
                errors.append(str(p.relative_to(root)) + ': ' + str(e))
        if p.suffix != '.md':
            continue
        try:
            text = p.read_text(encoding='utf-8-sig')
        except UnicodeError as e:
            errors.append(str(p.relative_to(root)) + ': ' + str(e))
            continue
        for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
            target = target.strip('<>')
            if re.match(r'^[a-z]+:', target, re.I) or target.startswith('#'):
                continue
            links += 1
            q = (p.parent / unquote(target.split('#')[0])).resolve()
            if not q.is_relative_to(root.resolve()) or not q.exists():
                errors.append('Nonportable or missing link: ' + str(p.relative_to(root)) + ' -> ' + target)
    for item in index:
        d = root / item['name']
        for name in ['skill.md', 'usage.md', 'validation.md']:
            if not (d / name).is_file():
                errors.append(item['name'] + ': missing ' + name)
        body = (d / 'skill.md').read_text(encoding='utf-8')
        front = re.match(r'^---\n(.*?)\n---\n', body, re.S)
        if not front or 'name: ' + item['name'] not in front.group(1) or 'description: ' not in front.group(1):
            errors.append(item['name'] + ': missing/wrong source frontmatter')
        if item['fresh_independent_reuse'] != 'NOT_RUN':
            errors.append(item['name'] + ': audit must not manufacture fresh reuse')
    for item in manifest:
        p = root / item['package_path']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != item['package_sha256']:
            errors.append('Source snapshot integrity failure: ' + item['id'])
        if item['copy_kind'] == 'byte_exact_original' and item['source_sha256'] != item['package_sha256']:
            errors.append('Claimed exact copy differs: ' + item['id'])
    return {
        'status': 'PASS_OFFLINE_DOCUMENT_AND_SNAPSHOT_INTEGRITY_ONLY' if not errors else 'FAIL',
        'skills_checked': len(index),
        'candidate_not_counted': 'fpga-uart-link-validation',
        'source_records_checked': len(manifest),
        'local_markdown_links_checked': links,
        'offline_checker_requires_original_workspace': False,
        'new_board_gpu_eda_operations': 0,
        'independent_behavioral_reuse': 'NOT_RUN',
        'missing_evidence_list': 'validation_gaps.md',
        'errors': errors,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(Path(__file__).resolve().parents[1])
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(rendered, encoding='utf-8')
    print(rendered)
    sys.exit(bool(result['errors']))
