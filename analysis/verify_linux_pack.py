"""Проверяет сопоставления импорта и комплектность инструкции; пакует результат."""

import ast
import importlib.util
import json
import re
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(r'D:\DemoExam')
support = root / 'exam_support'
spec = importlib.util.spec_from_file_location('exam_import', support / 'prepare_import.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sql, counts = module.build_seed(root / 'КИМ_ДЭ_09.02.07-2')
expected = {'roles': 3, 'users': 20, 'products': 31, 'sizes': 35, 'stock_items': 92, 'orders': 10, 'order_items': 30, 'available_pairs': 1274, 'ordered_pairs': 36}
assert counts == expected, (counts, expected)
assert module.model_key('Кроссовки «Азимут Бег» ', 'Азимут') == ('Кроссовки «Азимут Бег»', 'Азимут')
assert module.model_key('Туфли женские натуральная кожа\u00a0с металлическими вставками', 'Кожевенные традиции')[0] == 'Туфли женские натуральная кожа с металлическими вставками'
assert module.model_key('Черные туфли в классическом стиле', 'Барбари')[0].endswith('база для деловых образов')
assert module.decimal_value('37.5') == module.decimal_value(37.5)
for value in ['0', '-1', '1.5', 'abc']:
    try:
        module.integer_value(value, minimum=1)
    except ValueError:
        pass
    else:
        raise AssertionError(f'Accepted invalid quantity: {value}')
for path in support.glob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
json.loads((support / 'config.example.json').read_text(encoding='utf-8'))
guide = (root / 'EXAM_LINUX_GUIDE.md').read_text(encoding='utf-8')
blocks = re.findall(r'```python\n(.*?)\n```', guide, flags=re.S)
for i, block in enumerate(blocks, 1):
    ast.parse(block, filename=f'guide_python_block_{i}')
assert guide.count('```') % 2 == 0
assert (support / 'database' / 'seed.sql').read_text(encoding='utf-8') == sql
with ZipFile(root / 'Exam_Linux_Pack.zip', 'w', compression=ZIP_DEFLATED) as archive:
    archive.write(root / 'EXAM_LINUX_GUIDE.md', 'EXAM_LINUX_GUIDE.md')
    for path in sorted(support.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            archive.write(path, path.relative_to(root).as_posix())
with ZipFile(root / 'Exam_Linux_Pack.zip') as archive:
    assert archive.testzip() is None
    print(json.dumps({'counts':counts, 'python_blocks_parsed':len(blocks), 'archive_files':archive.namelist()}, ensure_ascii=False, indent=2))
