from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import ast
import re

root = Path(r'D:\DemoExam')
guide = (root / 'EXAM_LINUX_GUIDE.md').read_text(encoding='utf-8')
blocks = re.findall(r'```python\n(.*?)\n```', guide, flags=re.S)
for number, block in enumerate(blocks, 1):
    ast.parse(block, filename=f'guide_example_{number}')
assert guide.count('```') % 2 == 0
for unwanted in ('requirements.in', 'pip freeze', 'check_environment.py', 'check_connection.py', 'exam_support', 'config.example.json'):
    assert unwanted not in guide, unwanted
assert 'python import_data.py' in guide
assert 'CREATE TABLE public.order_items' in guide
assert 'def import_data():' in guide

with ZipFile(root / 'Exam_Linux_Pack.zip', 'w', compression=ZIP_DEFLATED) as archive:
    archive.write(root / 'EXAM_LINUX_GUIDE.md', 'EXAM_LINUX_GUIDE.md')
    for path in sorted((root / 'exam_support').rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            archive.write(path, path.relative_to(root).as_posix())
with ZipFile(root / 'Exam_Linux_Pack.zip') as archive:
    assert archive.testzip() is None
    assert not any(name.endswith('.in') for name in archive.namelist())
    assert archive.read('EXAM_LINUX_GUIDE.md').decode('utf-8') == guide
print(f'Guide examples parsed: {len(blocks)}; archive rebuilt successfully')
