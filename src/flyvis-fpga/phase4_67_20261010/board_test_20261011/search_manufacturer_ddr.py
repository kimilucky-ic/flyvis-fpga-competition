"""Search targeted local manufacturer sources only; no tools/board changes."""
import hashlib
import json
from pathlib import Path
import time
from pypdf import PdfReader

source = Path('D:/BaiduNetdiskDownload/正点原子')
OUTPUT = Path(__file__).resolve().parent / ('DDR_SOURCE_REVIEW_' + time.strftime('%Y%m%d_%H%M%S'))
OUTPUT.mkdir(exist_ok=False)
DOCS = [
    '2_文档教程/2_【正点原子】领航者ZYNQ之嵌入式Vitis开发指南V1.2.pdf',
    '2_文档教程/5_【正点原子】领航者ZYNQ之PYNQ开发指南_V3.2.pdf',
    '7_芯片数据手册/03_DDR3/4Gb_DDR3_E_Die_component_Datasheet.PDF',
]
KEYS = ('MT41K256', 'MT41J256', 'NT5CC256', 'BANK1', 'Bank 1', 'NT5CC128')
rows = []
for relative in DOCS:
    path = source / relative
    reader = PdfReader(path)
    pages = []
    for index, page in enumerate(reader.pages):
        content = page.extract_text() or ''
        matches = [key for key in KEYS if key.lower() in content.lower()]
        if matches:
            pages.append({'pdf_page': index + 1, 'matched_terms': matches, 'text': content})
    rows.append({'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                 'page_count': len(reader.pages), 'matched_pages': pages})
    print(relative, 'pages', len(reader.pages), 'matches', [p['pdf_page'] for p in pages], flush=True)
notes = []
for relative in ('3_开发板原理图和硬件相关文件/硬件相关文件/硬件改版说明/核心板改版说明.txt',
                 '3_开发板原理图和硬件相关文件/硬件相关文件/硬件改版说明/底板改版说明.txt'):
    path = source / relative
    raw = path.read_bytes()
    notes.append({'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(),
                  'encoding_used': 'gb18030', 'text': raw.decode('gb18030', errors='replace')})
report = {'status': 'READ_ONLY_MANUFACTURER_SOURCE_SEARCH', 'board_io_operations': 0,
          'source_root': str(source), 'pdf_sources': rows, 'revision_notes': notes,
          'physical_board_revision': 'PENDING_USER_PHOTO',
          'does_not_approve_board_load_or_new_boot_image': True}
(OUTPUT / 'SOURCE_SEARCH.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('SOURCE_REPORT', str(OUTPUT.resolve()), flush=True)
