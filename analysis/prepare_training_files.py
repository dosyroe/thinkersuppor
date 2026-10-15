from pathlib import Path
import re
import shutil
from zipfile import ZipFile

root = Path(r'D:\DemoExam')
project = root / 'training_project'
source = root / 'КИМ_ДЭ_09.02.07-2'
(project / 'database').mkdir(exist_ok=True)
shutil.copy2(root / 'exam_support/database/schema.sql', project / 'database/schema.sql')
shutil.copy2(root / 'exam_support/database/check_import.sql', project / 'database/check_import.sql')
(project / 'data').mkdir(exist_ok=True)
for name in ['Products_import.xlsx', 'Sizes_import.xlsx', 'Users_import.xlsx', 'Stock_Items_import.xlsx', 'Orders_import.xlsx']:
    matches = list(source.rglob(name))
    assert len(matches) == 1
    shutil.copy2(matches[0], project / 'data' / name)
assets = next(source.rglob('picture.png')).parent
(project / 'assets/products').mkdir(parents=True, exist_ok=True)
for image in (assets / 'Images').glob('*.png'):
    shutil.copy2(image, project / 'assets/products' / image.name)
shutil.copy2(assets / 'picture.png', project / 'assets/picture.png')
shutil.copy2(assets / 'Чудо Обувь.png', project / 'assets/logo.png')
shutil.copy2(assets / 'Чудо Обувь.ico', project / 'assets/app.ico')

# Переносим полный прямой импорт из ранее написанной инструкции в запускаемый проект.
guide = (root / 'EXAM_LINUX_GUIDE.md').read_text(encoding='utf-8')
blocks = re.findall(r'```python\n(.*?)\n```', guide, flags=re.S)
code = next(block for block in blocks if 'def import_data():' in block)
code = code.replace('from app.db import get_connection', 'from app.db import get_connection\nimport psycopg')
code = code.replace('return cursor.fetchone()[0]', 'return next(iter(cursor.fetchone().values()))')
code = code.replace('SELECT COUNT(*) FROM roles', 'SELECT COUNT(*) AS total FROM roles')
code = code.replace('cursor.fetchone()[0] != 0', 'cursor.fetchone()["total"] != 0')
code = code.replace('int(quantity)', 'whole_number(quantity)')
code = code.replace('def model_key(name, manufacturer):', '''def whole_number(value):
    number_value = number(value)
    if number_value != number_value.to_integral_value() or number_value < 0:
        raise ValueError(f"Ожидалось целое неотрицательное число: {value}")
    return int(number_value)


def model_key(name, manufacturer):''')
code = code.replace('if __name__ == "__main__":\n    import_data()', '''if __name__ == "__main__":
    try:
        import_data()
    except (ValueError, KeyError, OSError, psycopg.Error) as error:
        raise SystemExit(f"Импорт не выполнен: {error}") from error''')
(project / 'import_data.py').write_text(code + '\n', encoding='utf-8')

pg_target = root / 'analysis/pg_runtime'
pg_target.mkdir(exist_ok=True)
with ZipFile(root / 'analysis/postgres-test.zip') as archive:
    names = [name for name in archive.namelist() if name.startswith(('pgsql/bin/', 'pgsql/share/', 'pgsql/lib/'))]
    for name in names:
        destination = (pg_target / name).resolve()
        if pg_target.resolve() not in destination.parents:
            raise ValueError(f'Archive path outside runtime: {name}')
        if not name.endswith('/'):
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(name) as input_file, destination.open('wb') as output_file:
                shutil.copyfileobj(input_file, output_file)
print(f'Training assets copied; extracted {len(names)} PostgreSQL runtime entries')
