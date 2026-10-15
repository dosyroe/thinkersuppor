"""Интеграционные проверки учебного приложения на временном PostgreSQL."""

import sys
from pathlib import Path
from datetime import date
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
import threading
import json
import uuid

root = Path(r'D:\DemoExam')
sys.path.insert(0, str(root / 'analysis/exam_test_deps'))
sys.path.insert(0, str(root / 'exam_project'))
import psycopg
from psycopg import sql
import settings

settings.DB_PORT = 55440
settings.DB_PASSWORD = ''
settings.DB_NAME = 'exam_test_' + uuid.uuid4().hex[:8]
with psycopg.connect(host='127.0.0.1', port=55440, user='postgres', dbname='postgres', autocommit=True) as conn:
    conn.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(settings.DB_NAME)))

from app import service
from app.db import get_connection
from app.common import month_bounds, parse_quantity, price_with_discount
from import_data import import_data

passed = []
def check(name, condition):
    if not condition:
        raise AssertionError(name)
    passed.append(name)

def query(statement, params=()):
    with get_connection() as conn:
        return conn.execute(statement, params).fetchall()

def execute(statement, params=()):
    with get_connection() as conn:
        conn.execute(statement, params)

def must_fail(name, action, error=ValueError):
    try:
        action()
    except error:
        passed.append(name)
    else:
        raise AssertionError('Expected failure: ' + name)

schema = (root / 'exam_project/database/schema.sql').read_text(encoding='utf-8')
with get_connection() as conn:
    conn.execute(schema, prepare=False)
import_data()
counts = {row['name']:row['total'] for row in query("""SELECT 'roles' AS name,COUNT(*) AS total FROM roles
    UNION ALL SELECT 'users',COUNT(*) FROM users UNION ALL SELECT 'products',COUNT(*) FROM products
    UNION ALL SELECT 'sizes',COUNT(*) FROM sizes UNION ALL SELECT 'stock_items',COUNT(*) FROM stock_items
    UNION ALL SELECT 'orders',COUNT(*) FROM orders UNION ALL SELECT 'order_items',COUNT(*) FROM order_items""")}
check('Import: all seven counts', counts == {'roles':3,'users':20,'products':31,'sizes':35,'stock_items':92,'orders':10,'order_items':30})
check('Available pairs 1274', query('SELECT SUM(quantity_available) AS total FROM stock_items')[0]['total'] == 1274)
check('Historical pairs 36', query('SELECT SUM(quantity) AS total FROM order_items')[0]['total'] == 36)
customer = service.login('asidorova')
manager = service.login('papetrov')
admin = service.login('isivanov')
check('Three roles', [u['role_code'] for u in (customer,manager,admin)] == ['customer','manager','admin'])
must_fail('Unknown login', lambda:service.login('nobody'))
must_fail('Parameterized login', lambda:service.login("asidorova' OR '1'='1"))
check('January calendar boundary', month_bounds(date(2027,1,20)) == (date(2026,12,1),date(2027,1,1)))
check('Discount exact Decimal', price_with_discount(Decimal('2190'),False) == Decimal('1642.50'))
for value in ['',0,-1,'1.5','abc',True]:
    must_fail(f'Invalid quantity {value!r}', lambda v=value:parse_quantity(v))
products = service.load_catalog(date(2026,10,13))
check('31 catalog models', len(products)==31)
check('Three low-stock models', len([p for p in products if p['total_quantity']<=3])==3)
check('October discounts', all(p['sale_price']==p['price']*Decimal('.75') for p in products))
may = service.load_catalog(date(2026,5,15))
check('Both discount branches in May', any(p['has_previous_orders'] for p in may) and any(not p['has_previous_orders'] for p in may))
must_fail('Customer cannot list orders', lambda:service.list_orders(customer['user_id']))
must_fail('Guest cannot order', lambda:service.create_order(None,{1:1}))
must_fail('Empty basket', lambda:service.create_order(customer['user_id'],{}))

# Preserve the genuine initial schema+data before exercising CRUD operations.
import subprocess
dump = root / 'exam_project/database/database_with_data.sql'
subprocess.run([str(root / 'analysis/exam_test_runtime/pgsql/bin/pg_dump.exe'), '-h', '127.0.0.1', '-p', '55440', '-U', 'postgres', '-d', settings.DB_NAME, '--no-owner', '--no-privileges', '--inserts', '-f', str(dump)], check=True)
restore_name = 'exam_restore_' + uuid.uuid4().hex[:8]
with psycopg.connect(host='127.0.0.1', port=55440, user='postgres', dbname='postgres', autocommit=True) as conn:
    conn.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(restore_name)))
subprocess.run([str(root / 'analysis/exam_test_runtime/pgsql/bin/psql.exe'), '-h', '127.0.0.1', '-p', '55440', '-U', 'postgres', '-d', restore_name, '-v', 'ON_ERROR_STOP=1', '-f', str(dump)], check=True, stdout=subprocess.DEVNULL)
with psycopg.connect(host='127.0.0.1', port=55440, user='postgres', dbname=restore_name) as conn:
    check('SQL dump restores actual initial orders and stock', conn.execute('SELECT (SELECT COUNT(*) FROM orders), (SELECT SUM(quantity_available) FROM stock_items)').fetchone() == (10, 1274))

before = {row['stock_item_id']:row['quantity_available'] for row in query('SELECT * FROM stock_items')}
order_id = service.create_order(customer['user_id'],{1:2,7:1},date(2026,10,13))
check('Sequence after imported IDs', order_id>10)
order,items = service.order_details(manager['user_id'],order_id)
check('Two-line order', len(items)==2)
check('Exact stock decrease', query('SELECT quantity_available FROM stock_items WHERE stock_item_id=1')[0]['quantity_available']==before[1]-2)
original_price = items[0]['unit_price']
execute('UPDATE products SET price=price+100 WHERE product_id=1')
check('Historical price preserved', service.order_details(manager['user_id'],order_id)[1][0]['unit_price']==original_price)
execute('UPDATE products SET price=price-100 WHERE product_id=1')
must_fail('Manager cannot edit order',lambda:service.edit_order(manager['user_id'],order_id,'2026-10-14',[]))
must_fail('Invalid date',lambda:service.edit_order(admin['user_id'],order_id,'2026-13-32',[]))
must_fail('Cannot edit alien item',lambda:service.edit_order(admin['user_id'],order_id,'2026-10-14',[1]))
must_fail('No empty saved order',lambda:service.edit_order(admin['user_id'],order_id,'2026-10-14',[i['order_item_id'] for i in items]))
service.edit_order(admin['user_id'],order_id,'2026-10-14',[items[0]['order_item_id']])
updated,remaining = service.order_details(manager['user_id'],order_id)
check('Admin edits date and removes line', updated['order_date']==date(2026,10,14) and len(remaining)==1)
check('Removed line restores quantity', query('SELECT quantity_available FROM stock_items WHERE stock_item_id=1')[0]['quantity_available']==before[1])
service.delete_order(manager['user_id'],order_id)
must_fail('Repeated delete cannot restore twice',lambda:service.delete_order(manager['user_id'],order_id))
check('Delete restores remaining stock', query('SELECT quantity_available FROM stock_items WHERE stock_item_id=7')[0]['quantity_available']==before[7])

count_before=query('SELECT COUNT(*) AS total FROM orders')[0]['total']
must_fail('Insufficient stock rollback',lambda:service.create_order(customer['user_id'],{1:1,7:99999}))
check('Rollback leaves no partial order',query('SELECT COUNT(*) AS total FROM orders')[0]['total']==count_before and query('SELECT quantity_available FROM stock_items WHERE stock_item_id=1')[0]['quantity_available']==before[1])
must_fail('CHECK constraint on quantity', lambda:execute('UPDATE stock_items SET quantity_available=-1 WHERE stock_item_id=1'), psycopg.Error)

execute('UPDATE stock_items SET quantity_available=1 WHERE stock_item_id=1')
barrier=threading.Barrier(2)
def buy_last_pair():
    barrier.wait()
    try:
        return service.create_order(customer['user_id'],{1:1})
    except ValueError:
        return None
with ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(lambda _:buy_last_pair(),range(2)))
check('Concurrent last pair: one winner',sum(value is not None for value in results)==1)
check('Concurrent stock never negative',query('SELECT quantity_available FROM stock_items WHERE stock_item_id=1')[0]['quantity_available']==0)
service.delete_order(manager['user_id'],next(value for value in results if value is not None))
execute('UPDATE stock_items SET quantity_available=%s WHERE stock_item_id=1',(before[1],))

# Создаём наши собственные Tk-виджеты скрыто; сообщения заменяем на журнал.
from app.ui import ShoeApp
from tkinter import ttk, messagebox
notifications=[]
for method in ('showinfo','showerror','showwarning'):
    setattr(messagebox,method,lambda *args,kind=method,**kwargs:notifications.append((kind,args)))
messagebox.askyesno=lambda *args,**kwargs:True
def children(widget):
    result=[]
    for child in widget.winfo_children():
        result.append(child)
        result.extend(children(child))
    return result
def button(app,text):
    return next(w for w in children(app.screen) if isinstance(w,ttk.Button) and w.cget('text')==text)

import importlib.util
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
app.show_login()
entry=next(w for w in children(app.screen) if isinstance(w,ttk.Entry))
entry.insert(0,'asidorova')
button(app,'Войти').invoke()
check('UI login callback',app.user['role_code']=='customer' and app.current_screen=='catalog')
app.sort_var.set('По убыванию')
app.category_var.set('Женская обувь')
app.search_var.set('КОЖА')
app.catalog_changed()
check('UI combined filters retain sorting',app.sort_var.get()=='По убыванию' and 0<len(app.catalog_scroll.inner.winfo_children())<31)
app.show_product(1)
button(app,'В корзину').invoke()
button(app,'В корзину').invoke()
check('UI merges repeated basket item',len(app.cart)==1 and next(iter(app.cart.values()))['quantity']==2)
app.show_product(2)
button(app,'В корзину').invoke()
check('UI multiple models',len(app.cart)==2)
app.show_cart()
tree=next(w for w in children(app.screen) if isinstance(w,ttk.Treeview))
check('UI basket has two rows',len(tree.get_children())==2)
button(app,'Подтвердить заказ').invoke()
check('UI checkout clears basket',not app.cart and app.current_screen=='catalog')
ui_order=query('SELECT MAX(order_id) AS id FROM orders')[0]['id']
app.user=manager
app.show_orders()
check('Manager no edit button',not any(isinstance(w,ttk.Button) and w.cget('text')=='Редактировать' for w in children(app.screen)))
tree=next(w for w in children(app.screen) if isinstance(w,ttk.Treeview))
tree.selection_set(str(ui_order))
messagebox.askyesno=lambda *args,**kwargs:False
button(app,'Удалить заказ').invoke()
check('UI canceled deletion unchanged',query('SELECT COUNT(*) AS total FROM orders WHERE order_id=%s',(ui_order,))[0]['total']==1)
messagebox.askyesno=lambda *args,**kwargs:True
app.user=admin
app.show_order_detail(ui_order,editing=True)
tree=next(w for w in children(app.screen) if isinstance(w,ttk.Treeview))
tree.selection_set(tree.get_children()[0])
button(app,'Удалить выбранную позицию').invoke()
entry=next(w for w in children(app.screen) if isinstance(w,ttk.Entry))
entry.delete(0,'end')
entry.insert(0,'2026-10-15')
button(app,'Сохранить').invoke()
check('UI admin saves edits',service.order_details(admin['user_id'],ui_order)[0]['order_date']==date(2026,10,15) and len(service.order_details(admin['user_id'],ui_order)[1])==1)
tree=next(w for w in children(app.screen) if isinstance(w,ttk.Treeview))
tree.selection_set(str(ui_order))
button(app,'Удалить заказ').invoke()
check('UI confirmed deletion refreshes list',app.current_screen=='orders' and not query('SELECT * FROM orders WHERE order_id=%s',(ui_order,)))
app.user = manager
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
app.show_catalog()
app.update_idletasks()
app.destroy()
check('No unexpected UI errors',not any(kind=='showerror' for kind,args in notifications))
check('End-to-end stock restored',query('SELECT SUM(quantity_available) AS total FROM stock_items')[0]['total']==1274)
report={'database':settings.DB_NAME,'postgresql':query('SELECT version() AS version')[0]['version'],'checks_passed':len(passed),'checks':passed}
(root/'analysis/exam_project_checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checks_passed':len(passed),'database':settings.DB_NAME},ensure_ascii=False))
