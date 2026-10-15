from pathlib import Path

root = Path(r"D:\DemoExam")
text = (root / "analysis/test_training_project.py").read_text(encoding="utf-8")
text = text.replace("analysis/test_deps", "analysis/exam_test_deps")
text = text.replace("training_project", "exam_project")
text = text.replace("from pglast import parse_sql\n", "")
text = text.replace("parse_sql(schema)\n", "")
text = text.replace("55439", "55440")
text = text.replace("chudo_test_", "exam_test_")
text = text.replace("analysis/training_checks.json", "analysis/exam_project_checks.json")
text = text.replace("for module in (2,3,4):\n", "for module in (2,3,4):\n")
start = text.index("for module in (2,3,4):")
end = text.index("app.show_login()", start)
text = text[:start] + '''import importlib.util
from zipfile import ZipFile
for stage, archive_name in [(2, 'Module_2_Catalog.zip'), (3, 'Module_3_Interface.zip'), (4, 'Module_4_Orders.zip')]:
    destination = root / 'analysis' / f'exam_run_stage_{stage}'
    with ZipFile(root / 'exam_versions' / archive_name) as archive:
        for entry in archive.infolist():
            if not (destination / entry.filename).resolve().is_relative_to(destination.resolve()):
                raise RuntimeError('Unexpected archive path')
        archive.extractall(destination)
    path = destination / 'chudo_obuv/app/ui.py'
    spec = importlib.util.spec_from_file_location(f'exam_ui_{stage}', path)
    ui = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ui)
    app = ui.ShoeApp()
    app.withdraw()
    app.update_idletasks()
    check(f'Tk stage {stage}: all cards', len(app.catalog_scroll.inner.winfo_children()) == 31)
    check(f'Tk stage {stage}: image references', all(any(hasattr(w, 'image') for w in children(card)) for card in app.catalog_scroll.inner.winfo_children()))
    check(f'Tk stage {stage}: no MODULE property', not hasattr(app, 'module'))
    if stage == 2:
        check('Stage 2 has no future login', not any(isinstance(w, ttk.Button) and w.cget('text') == 'Войти' for w in children(app.screen)))
    else:
        check(f'Stage {stage}: guest search displayed', any(isinstance(w, ttk.Entry) for w in children(app.screen)))
        app.sort_var.set('По убыванию')
        app.category_var.set('Женская обувь')
        app.search_var.set('КОЖА')
        app.catalog_changed()
        check(f'Stage {stage}: guest combined filtering', app.user is None and 0 < len(app.catalog_scroll.inner.winfo_children()) < 31 and app.sort_var.get() == 'По убыванию')
        must_fail(f'Stage {stage}: guest cannot view/order model', lambda: app.show_product(1))
        if stage == 3:
            app.user = manager
            app.show_catalog()
            check('Stage 3 has no future orders button', not any(isinstance(w, ttk.Button) and w.cget('text') == 'Заказы' for w in children(app.screen)))
    app.destroy()

app = ShoeApp()
app.withdraw()
''' + text[end:]
addition_point = "before = {row['stock_item_id']"
index = text.index(addition_point)
text = text[:index] + '''# Preserve the genuine initial schema+data before exercising CRUD operations.
import subprocess
dump = root / 'exam_project/database/database_with_data.sql'
subprocess.run([str(root / 'analysis/exam_test_runtime/pgsql/bin/pg_dump.exe'), '-h', '127.0.0.1', '-p', '55440', '-U', 'postgres', '-d', settings.DB_NAME, '--no-owner', '--no-privileges', '--inserts', '-f', str(dump)], check=True)
restore_name = 'exam_restore_' + uuid.uuid4().hex[:8]
with psycopg.connect(host='127.0.0.1', port=55440, user='postgres', dbname='postgres', autocommit=True) as conn:
    conn.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(restore_name)))
subprocess.run([str(root / 'analysis/exam_test_runtime/pgsql/bin/psql.exe'), '-h', '127.0.0.1', '-p', '55440', '-U', 'postgres', '-d', restore_name, '-v', 'ON_ERROR_STOP=1', '-f', str(dump)], check=True, stdout=subprocess.DEVNULL)
with psycopg.connect(host='127.0.0.1', port=55440, user='postgres', dbname=restore_name) as conn:
    check('SQL dump restores actual initial orders and stock', conn.execute('SELECT (SELECT COUNT(*) FROM orders), (SELECT SUM(quantity_available) FROM stock_items)').fetchone() == (10, 1274))

''' + text[index:]
# Testing manager addition through the existing catalogue/cart route.
index = text.index("app.show_catalog()\napp.update_idletasks()\napp.destroy()", text.index("check('UI confirmed deletion"))
text = text[:index] + '''app.user = manager
app.show_orders()
button(app, 'Новый заказ').invoke()
check('Manager new-order route opens catalogue', app.current_screen == 'catalog')
app.show_product(1)
button(app, 'В корзину').invoke()
app.show_cart()
button(app, 'Подтвердить заказ').invoke()
check('Manager checkout refreshes orders list', app.current_screen == 'orders' and not app.cart)
manager_order = query('SELECT MAX(order_id) AS id FROM orders')[0]['id']
service.delete_order(manager['user_id'], manager_order)
''' + text[index:]
(root / 'analysis/test_exam_project.py').write_text(text, encoding='utf-8')
print('Dedicated exam tests prepared')
