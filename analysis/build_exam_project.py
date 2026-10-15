"""Создаёт отдельный экзаменационный пример, сохраняя учебные файлы."""

from pathlib import Path
import ast
import hashlib
import json
import shutil

ROOT = Path(r"D:\DemoExam")
TRAINING = ROOT / "training_project"
PROJECT = ROOT / "exam_project"
STAGES = ROOT / "analysis" / "exam_stages"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def method_replace(code, name, replacement):
    tree = ast.parse(code)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ShoeApp")
    node = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == name)
    lines = code.splitlines(keepends=True)
    return "".join(lines[:node.lineno - 1]) + replacement.rstrip() + "\n" + "".join(lines[node.end_lineno:])


def only_functions(code, names):
    tree = ast.parse(code)
    lines = code.splitlines(keepends=True)
    return "\n\n".join("".join(lines[n.lineno-1:n.end_lineno]).rstrip()
                       for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names) + "\n"


def remove_methods(code, names):
    tree = ast.parse(code)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ShoeApp")
    lines = code.splitlines(keepends=True)
    for node in reversed(cls.body):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            del lines[node.lineno-1:node.end_lineno]
    return "".join(lines)


learning_files = [ROOT / "EXAM_LINUX_GUIDE.md", ROOT / "Exam_Linux_Pack.zip"]
learning_files += [p for p in TRAINING.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in learning_files}
write(ROOT / "analysis" / "exam_learning_hashes.json", json.dumps(hashes, ensure_ascii=False, indent=2))

PROJECT.mkdir(exist_ok=True)
for name in ["requirements.txt", ".gitignore", "import_data.py", "app/__init__.py", "app/db.py", "app/common.py", "app/service.py", "database/schema.sql"]:
    target = PROJECT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TRAINING / name, target)
for folder in ["data", "assets"]:
    shutil.copytree(TRAINING / folder, PROJECT / folder, dirs_exist_ok=True)

write(PROJECT / "settings.py", '''DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_NAME = "chudo_obuv"
DB_USER = "postgres"
DB_PASSWORD = "ВПИШИ_ПАРОЛЬ_POSTGRESQL"
''')
write(PROJECT / "main.py", '''from app.ui import ShoeApp


if __name__ == "__main__":
    application = ShoeApp()
    application.mainloop()
''')

ui = (TRAINING / "app/ui.py").read_text(encoding="utf-8")
ui = ui.replace("def __init__(self, module=4, start=True):", "def __init__(self):")
ui = ui.replace('''        if module not in (2, 3, 4):
            self.destroy()
            raise ValueError("MODULE должен быть 2, 3 или 4")
        self.module = module
''', "")
ui = ui.replace("        if start:\n            self.safe(self.show_catalog)", "        self.safe(self.show_catalog)")
ui = ui.replace("        if self.module < 4 or self.user is None:", "        if self.user is None:")
ui = ui.replace("Работа с заказами доступна в модуле 4 менеджеру и администратору", "Работа с заказами доступна менеджеру и администратору после входа")
ui = ui.replace("        product, sizes = service.product_details(product_id)\n", '''        if self.user is None:
            raise ValueError("Для просмотра модели и оформления заказа войдите по логину")
        product, sizes = service.product_details(product_id)
''', 1)

catalog = '''    def show_catalog(self):
        self.products = service.load_catalog()
        self.change_screen("catalog", "Каталог")
        self.make_header("Чудо Обувь")
        toolbar = tk.Frame(self.screen, bg=WHITE, padx=12, pady=8)
        toolbar.pack(fill="x")
        logo = self.picture(None, (80, 65), logo=True)
        logo_label = tk.Label(toolbar, image=logo, bg=WHITE)
        logo_label.image = logo
        logo_label.pack(side="left", padx=(0, 12))
        if self.user is None:
            ttk.Button(toolbar, text="Войти", style="Action.TButton", command=self.show_login).pack(side="right")
        else:
            ttk.Button(toolbar, text="Выйти", command=self.logout).pack(side="right")
            ttk.Button(toolbar, text=f"Корзина ({sum(item['quantity'] for item in self.cart.values())})", style="Action.TButton", command=self.show_cart).pack(side="right", padx=8)
            if self.user["role_code"] in ("manager", "admin"):
                ttk.Button(toolbar, text="Заказы", command=lambda: self.safe(self.show_orders)).pack(side="right")
        controls = tk.Frame(self.screen, bg=WHITE, padx=12, pady=4)
        controls.pack(fill="x")
        ttk.Label(controls, text="Поиск:").pack(side="left")
        ttk.Entry(controls, textvariable=self.search_var, width=25).pack(side="left", padx=6)
        categories = ["Все категории"] + sorted({row["category"] for row in self.products})
        category_box = ttk.Combobox(controls, textvariable=self.category_var, values=categories, state="readonly", width=23)
        category_box.pack(side="left", padx=6)
        category_box.bind("<<ComboboxSelected>>", self.catalog_changed)
        sort_box = ttk.Combobox(controls, textvariable=self.sort_var, values=["По возрастанию", "По убыванию"], state="readonly", width=19)
        sort_box.pack(side="left", padx=6)
        sort_box.bind("<<ComboboxSelected>>", self.catalog_changed)
        self.result_label = ttk.Label(self.screen)
        self.result_label.pack(anchor="w", padx=14, pady=4)
        self.catalog_scroll = ScrollFrame(self.screen)
        self.catalog_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.current_scroll = self.catalog_scroll
        self.render_catalog()
'''
ui = method_replace(ui, "show_catalog", catalog)

# Both the controls and their application are independent of authorization.
ui = ui.replace('''        if self.module >= 3 and self.user:
            query = self.search_var.get().strip().casefold()
            category = self.category_var.get()
            rows = [row for row in rows if (category == "Все категории" or row["category"] == category)
                    and (not query or query in row["product_name"].casefold() or query in row["description"].casefold())]
            rows.sort(key=lambda row: (row["sale_price"], row["product_id"]), reverse=self.sort_var.get() == "По убыванию")
''', '''        query = self.search_var.get().strip().casefold()
        category = self.category_var.get()
        rows = [row for row in rows if (category == "Все категории" or row["category"] == category)
                and (not query or query in row["product_name"].casefold() or query in row["description"].casefold())]
        rows.sort(key=lambda row: (row["sale_price"], row["product_id"]), reverse=self.sort_var.get() == "По убыванию")
''')
ui = ui.replace("            if self.module >= 3:\n                self.bind_card(card, product[\"product_id\"])", "            self.bind_card(card, product[\"product_id\"])")
ui = ui.replace('''            info.pack(side="left", fill="both", expand=True)
''', '''            info.pack(side="left", fill="both", expand=True)

            def resize_text(event, panel=info):
                for label in panel.winfo_children():
                    label.configure(wraplength=max(120, event.width))

            info.bind("<Configure>", resize_text)
''')
assert "self.module" not in ui and "MODULE" not in ui
ast.parse(ui)
write(PROJECT / "app/ui.py", ui)

order_methods = {"show_orders", "show_order_detail"}
third = remove_methods(ui, order_methods)
third = third.replace('''            if self.user["role_code"] in ("manager", "admin"):
                ttk.Button(toolbar, text="Заказы", command=lambda: self.safe(self.show_orders)).pack(side="right")
''', "")
third = third.replace("        self.return_to_orders = False\n", "")
third = third.replace('''        if self.return_to_orders:
                self.show_orders()
        else:
            self.show_catalog()
''', "        self.show_catalog()\n")
# Remove the branch as a complete method replacement, preserving its actions.
third = method_replace(third, "confirm_cart", '''    def confirm_cart(self):
        if self.user is None:
            raise ValueError("Сначала войдите в систему")
        quantities = {stock_id: item["quantity"] for stock_id, item in self.cart.items()}
        order_id = service.create_order(self.user["user_id"], quantities)
        self.cart.clear()
        messagebox.showinfo("Заказ оформлен", f"Заказ №{order_id} сохранён", parent=self)
        self.show_catalog()
''')
ast.parse(third)
write(STAGES / "3/app/ui.py", third)
service = (PROJECT / "app/service.py").read_text(encoding="utf-8")
third_service = service[:service.index("\ndef list_orders(")].rstrip() + "\n"
write(STAGES / "3/app/service.py", third_service)

second = remove_methods(ui, {"catalog_changed", "bind_card", "show_login", "logout", "show_product", "make_table", "selected_id", "show_cart", "cancel_cart", "confirm_cart", "show_orders", "show_order_detail"})
second = second.replace("from decimal import Decimal\n", "")
second = second.replace("from app.common import money, parse_quantity, size_text", "from app.common import money")
for line in ['        self.cart = {}\n', '        self.return_to_orders = False\n',
             '        self.search_var = tk.StringVar()\n', '        self.category_var = tk.StringVar(value="Все категории")\n',
             '        self.sort_var = tk.StringVar(value="По возрастанию")\n',
             '        self.search_var.trace_add("write", self.catalog_changed)\n']:
    second = second.replace(line, "")
second_catalog = catalog[:catalog.index("        if self.user is None:")] + catalog[catalog.index("        self.result_label ="):]
second = method_replace(second, "show_catalog", second_catalog)
second = second.replace('''        query = self.search_var.get().strip().casefold()
        category = self.category_var.get()
        rows = [row for row in rows if (category == "Все категории" or row["category"] == category)
                and (not query or query in row["product_name"].casefold() or query in row["description"].casefold())]
        rows.sort(key=lambda row: (row["sale_price"], row["product_id"]), reverse=self.sort_var.get() == "По убыванию")
''', "")
second = second.replace('            self.bind_card(card, product["product_id"])\n', "")
second = method_replace(second, "close_app", '''    def close_app(self):
        self.destroy()
''')
ast.parse(second)
write(STAGES / "2/app/ui.py", second)
second_service = '''from datetime import date

from app.common import month_bounds, price_with_discount
from app.db import get_connection


''' + only_functions(service, {"load_catalog"})
write(STAGES / "2/app/service.py", second_service)
common = (PROJECT / "app/common.py").read_text(encoding="utf-8")
second_common = '''from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP


''' + only_functions(common, {"month_bounds", "price_with_discount", "money"})
write(STAGES / "2/app/common.py", second_common)
for folder in ["2", "3"]:
    for path in (STAGES / folder).rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
print("Separate exam project created; stages 2/3 are real source versions without MODULE")
