"""Все окна приложения. Здесь создаются виджеты и вызываются функции service."""

from pathlib import Path
from decimal import Decimal
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

import psycopg
from PIL import Image, ImageTk

from app import service
from app.common import money, parse_quantity, size_text

ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "assets"
WHITE = "#FFFFFF"
EXTRA = "#D2F6E7"
ACCENT = "#70B2AF"
LOW_STOCK = "#ff8080"


class ScrollFrame(tk.Frame):
    """Canvas прокручивает внутренний Frame с карточками."""

    def __init__(self, parent):
        super().__init__(parent, bg=WHITE)
        self.canvas = tk.Canvas(self, bg=WHITE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=WHITE)
        self.window_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self.update_scrollregion)
        self.canvas.bind("<Configure>", self.update_width)

    def update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_width(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)


class ShoeApp(tk.Tk):
    def __init__(self, module=4, start=True):
        super().__init__()
        if module not in (2, 3, 4):
            self.destroy()
            raise ValueError("MODULE должен быть 2, 3 или 4")
        self.module = module
        self.user = None
        self.cart = {}
        self.products = []
        self.current_screen = ""
        self.current_scroll = None
        self.return_to_orders = False
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Все категории")
        self.sort_var = tk.StringVar(value="По возрастанию")
        self.title("Чудо Обувь — Каталог")
        self.geometry("1100x720")
        self.minsize(900, 580)
        self.configure(bg=WHITE)
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            tkfont.nametofont(name).configure(family="Calibri", size=11)
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TButton", font=("Calibri", 11), padding=7)
        style.configure("Action.TButton", background=ACCENT)
        style.configure("TLabel", background=WHITE, font=("Calibri", 11))
        style.configure("Treeview", font=("Calibri", 11), rowheight=30)
        style.configure("Treeview.Heading", font=("Calibri", 11, "bold"))
        self.screen = tk.Frame(self, bg=WHITE)
        self.screen.pack(fill="both", expand=True)
        self.search_var.trace_add("write", self.catalog_changed)
        self.bind("<MouseWheel>", self.scroll_wheel)
        self.bind("<Button-4>", self.scroll_wheel)
        self.bind("<Button-5>", self.scroll_wheel)
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        try:
            with Image.open(ASSETS_DIR / "app.ico") as source:
                self.app_icon = ImageTk.PhotoImage(source.convert("RGBA"))
            self.iconphoto(True, self.app_icon)
        except (OSError, tk.TclError):
            pass
        if start:
            self.safe(self.show_catalog)

    def safe(self, action):
        """Ошибка операции показывается пользователю, а не закрывает приложение."""
        try:
            return action()
        except ValueError as error:
            messagebox.showerror("Проверьте данные", str(error), parent=self)
        except psycopg.Error as error:
            print("Ошибка PostgreSQL:", error)
            messagebox.showerror("Ошибка базы данных", "Операция не выполнена. Проверьте запуск PostgreSQL и параметры settings.py, затем повторите действие.", parent=self)
        except OSError as error:
            messagebox.showerror("Ошибка файла", f"Не удалось прочитать ресурс: {error}. Проверьте папку assets.", parent=self)
        return None

    def change_screen(self, name, title):
        self.current_screen = name
        self.current_scroll = None
        self.title("Чудо Обувь — " + title)
        for child in self.screen.winfo_children():
            child.destroy()

    def make_header(self, title, back=None):
        header = tk.Frame(self.screen, bg=EXTRA, padx=12, pady=10)
        header.pack(fill="x")
        if back is not None:
            ttk.Button(header, text="← Назад", command=lambda: self.safe(back)).pack(side="left", padx=(0, 12))
        tk.Label(header, text=title, bg=EXTRA, font=("Calibri", 18, "bold")).pack(side="left")
        fio = "Гость"
        if self.user:
            fio = " ".join(self.user[key] for key in ("last_name", "first_name", "middle_name"))
        tk.Label(header, text=fio, bg=EXTRA, wraplength=340).pack(side="right")

    def picture(self, filename, box=(140, 110), logo=False):
        path = ASSETS_DIR / "logo.png" if logo else ASSETS_DIR / "products" / (filename or "")
        try:
            with Image.open(path) as source:
                image = source.convert("RGBA")
        except (OSError, ValueError):
            with Image.open(ASSETS_DIR / "picture.png") as source:
                image = source.convert("RGBA")
        image.thumbnail(box)
        return ImageTk.PhotoImage(image)

    def show_catalog(self):
        self.products = service.load_catalog()
        self.change_screen("catalog", "Каталог")
        self.make_header("Чудо Обувь")
        toolbar = tk.Frame(self.screen, bg=WHITE, padx=12, pady=8)
        toolbar.pack(fill="x")
        logo = self.picture(None, (80, 65), logo=True)
        logo_label = tk.Label(toolbar, image=logo, bg=WHITE)
        logo_label.image = logo
        logo_label.pack(side="left", padx=(0, 12))
        ttk.Button(toolbar, text="Обновить каталог", command=lambda: self.safe(self.show_catalog)).pack(side="left")
        if self.module >= 3:
            if self.user is None:
                ttk.Button(toolbar, text="Войти", style="Action.TButton", command=self.show_login).pack(side="right")
            else:
                ttk.Button(toolbar, text="Выйти", command=self.logout).pack(side="right")
                ttk.Button(toolbar, text=f"Корзина ({sum(item['quantity'] for item in self.cart.values())})", style="Action.TButton", command=self.show_cart).pack(side="right", padx=8)
                if self.module >= 4 and self.user["role_code"] in ("manager", "admin"):
                    ttk.Button(toolbar, text="Заказы", command=lambda: self.safe(self.show_orders)).pack(side="right")
        controls = tk.Frame(self.screen, bg=WHITE, padx=12, pady=4)
        controls.pack(fill="x")
        if self.module >= 3 and self.user:
            ttk.Label(controls, text="Поиск:").pack(side="left")
            ttk.Entry(controls, textvariable=self.search_var, width=25).pack(side="left", padx=6)
            categories = ["Все категории"] + sorted({row["category"] for row in self.products})
            category_box = ttk.Combobox(controls, textvariable=self.category_var, values=categories, state="readonly", width=23)
            category_box.pack(side="left", padx=6)
            category_box.bind("<<ComboboxSelected>>", self.catalog_changed)
            sort_box = ttk.Combobox(controls, textvariable=self.sort_var, values=["По возрастанию", "По убыванию"], state="readonly", width=19)
            sort_box.pack(side="left", padx=6)
            sort_box.bind("<<ComboboxSelected>>", self.catalog_changed)
        else:
            ttk.Label(controls, text="Каталог моделей обуви").pack(side="left")
        self.result_label = ttk.Label(self.screen)
        self.result_label.pack(anchor="w", padx=14, pady=4)
        self.catalog_scroll = ScrollFrame(self.screen)
        self.catalog_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.current_scroll = self.catalog_scroll
        self.render_catalog()

    def catalog_changed(self, *args):
        if self.current_screen == "catalog" and hasattr(self, "catalog_scroll"):
            self.render_catalog()

    def render_catalog(self):
        for child in self.catalog_scroll.inner.winfo_children():
            child.destroy()
        rows = list(self.products)
        if self.module >= 3 and self.user:
            query = self.search_var.get().strip().casefold()
            category = self.category_var.get()
            rows = [row for row in rows if (category == "Все категории" or row["category"] == category)
                    and (not query or query in row["product_name"].casefold() or query in row["description"].casefold())]
            rows.sort(key=lambda row: (row["sale_price"], row["product_id"]), reverse=self.sort_var.get() == "По убыванию")
        self.result_label.configure(text=f"Показано моделей: {len(rows)} из {len(self.products)}")
        for product in rows:
            color = LOW_STOCK if product["total_quantity"] <= 3 else WHITE
            card = tk.Frame(self.catalog_scroll.inner, bg=color, bd=1, relief="solid", padx=10, pady=10)
            card.pack(fill="x", pady=5)
            photo = self.picture(product["image_path"])
            photo_label = tk.Label(card, image=photo, bg=color, width=150)
            photo_label.image = photo
            photo_label.pack(side="left", padx=(0, 10))
            price_label = tk.Label(card, text=money(product["sale_price"]), bg=color, font=("Calibri", 16, "bold"), width=14)
            price_label.pack(side="right", padx=6)
            info = tk.Frame(card, bg=color)
            info.pack(side="left", fill="both", expand=True)
            title = tk.Label(info, text=product["manufacturer"] + " | " + product["product_name"], bg=color,
                             font=("Calibri", 12, "bold"), anchor="w", justify="left", wraplength=560)
            title.pack(fill="x")
            for text in (product["category"], f"Количество: {product['total_quantity']}", "Состав: " + product["composition"]):
                tk.Label(info, text=text, bg=color, anchor="w", justify="left", wraplength=560).pack(fill="x", pady=2)
            if self.module >= 3:
                self.bind_card(card, product["product_id"])
        self.catalog_scroll.canvas.yview_moveto(0)

    def bind_card(self, widget, product_id):
        widget.bind("<Button-1>", lambda event, pid=product_id: self.safe(lambda: self.show_product(pid)))
        for child in widget.winfo_children():
            self.bind_card(child, product_id)

    def scroll_wheel(self, event):
        if self.current_scroll is None:
            return
        if getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0:
            direction = -1
        else:
            direction = 1
        self.current_scroll.canvas.yview_scroll(direction, "units")

    def show_login(self):
        self.change_screen("login", "Вход")
        self.make_header("Вход по логину", self.show_catalog)
        form = tk.Frame(self.screen, bg=WHITE, padx=30, pady=30)
        form.pack(anchor="n")
        ttk.Label(form, text="Введите логин из списка пользователей. Пароль не нужен.").pack(pady=12)
        login_var = tk.StringVar()
        entry = ttk.Entry(form, textvariable=login_var, width=35)
        entry.pack(pady=8)

        def perform_login():
            self.user = service.login(login_var.get())
            self.show_catalog()

        ttk.Button(form, text="Войти", style="Action.TButton", command=lambda: self.safe(perform_login)).pack(pady=12)
        entry.bind("<Return>", lambda event: self.safe(perform_login))
        entry.focus_set()

    def logout(self):
        if self.cart and not messagebox.askyesno("Выход", "Незавершённая корзина будет очищена. Выйти?", parent=self):
            return
        self.user = None
        self.cart.clear()
        self.search_var.set("")
        self.category_var.set("Все категории")
        self.return_to_orders = False
        self.safe(self.show_catalog)

    def show_product(self, product_id):
        product, sizes = service.product_details(product_id)
        self.change_screen("product", "Просмотр модели")
        self.make_header("Модель обуви", self.show_catalog)
        scroll = ScrollFrame(self.screen)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        self.current_scroll = scroll
        body = scroll.inner
        photo = self.picture(product["image_path"], (270, 220))
        photo_label = tk.Label(body, image=photo, bg=WHITE)
        photo_label.image = photo
        photo_label.pack(pady=8)
        text_rows = [product["product_name"], "Производство: " + product["manufacturer"],
                     "Категория: " + product["category"], "Цена: " + money(product["sale_price"]),
                     "Состав: " + product["composition"], "Описание: " + product["description"],
                     "Размерный ряд: " + ", ".join(size_text(row["size_value"]) for row in sizes)]
        for text in text_rows:
            tk.Label(body, text=text, bg=WHITE, wraplength=820, justify="left", anchor="w").pack(fill="x", pady=5)
        available = {f"{size_text(row['size_value'])} — доступно {row['quantity_available']}": row
                     for row in sizes if row["quantity_available"] > 0}
        if not available:
            ttk.Label(body, text="Сейчас нет доступных размеров").pack(pady=12)
            return
        controls = tk.Frame(body, bg=WHITE)
        controls.pack(fill="x", pady=15)
        ttk.Label(controls, text="Размер:").pack(side="left")
        size_var = tk.StringVar(value=next(iter(available)))
        ttk.Combobox(controls, textvariable=size_var, values=list(available), state="readonly", width=27).pack(side="left", padx=8)
        ttk.Label(controls, text="Количество:").pack(side="left")
        quantity_var = tk.StringVar(value="1")
        ttk.Entry(controls, textvariable=quantity_var, width=8).pack(side="left", padx=8)

        def add():
            if self.user is None:
                raise ValueError("Для оформления заказа войдите по логину")
            quantity = parse_quantity(quantity_var.get())
            stock = available[size_var.get()]
            stock_id = stock["stock_item_id"]
            old_quantity = self.cart.get(stock_id, {}).get("quantity", 0)
            if quantity + old_quantity > stock["quantity_available"]:
                raise ValueError(f"В выбранном размере доступно {stock['quantity_available']} пар, в корзине уже {old_quantity}")
            self.cart[stock_id] = {"product_id": product_id, "product_name": product["product_name"],
                                   "manufacturer": product["manufacturer"], "size_value": stock["size_value"],
                                   "quantity": quantity + old_quantity, "unit_price": product["sale_price"]}
            messagebox.showinfo("Корзина", "Товар добавлен в корзину", parent=self)

        ttk.Button(controls, text="В корзину", style="Action.TButton", command=lambda: self.safe(add)).pack(side="left", padx=8)
        ttk.Button(body, text="Открыть корзину", command=self.show_cart).pack(anchor="w", pady=10)

    def make_table(self, parent, columns):
        holder = tk.Frame(parent, bg=WHITE)
        holder.pack(fill="both", expand=True, padx=12, pady=10)
        names = [name for name, title, width in columns]
        tree = ttk.Treeview(holder, columns=names, show="headings", selectmode="browse")
        for name, title, width in columns:
            tree.heading(name, text=title)
            tree.column(name, width=width, minwidth=60, stretch=name == "model")
        vertical = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(holder, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        holder.rowconfigure(0, weight=1)
        holder.columnconfigure(0, weight=1)
        return tree

    def selected_id(self, tree):
        selected = tree.selection()
        if not selected:
            raise ValueError("Сначала выберите строку в таблице")
        return int(selected[0])

    def show_cart(self):
        if self.user is None:
            messagebox.showwarning("Вход необходим", "Сначала войдите по логину", parent=self)
            return
        self.change_screen("cart", "Корзина")
        self.make_header("Корзина", self.show_catalog)
        tree = self.make_table(self.screen, [("model", "Модель / производство", 470), ("size", "Размер", 90),
                               ("quantity", "Пар", 70), ("price", "Цена за пару", 130), ("total", "Сумма", 130)])
        total = Decimal("0")
        for stock_id, item in self.cart.items():
            line_total = item["quantity"] * item["unit_price"]
            total += line_total
            tree.insert("", "end", iid=str(stock_id), values=(item["product_name"] + " / " + item["manufacturer"],
                        size_text(item["size_value"]), item["quantity"], money(item["unit_price"]), money(line_total)))
        ttk.Label(self.screen, text="Итого: " + money(total)).pack(anchor="e", padx=15, pady=8)
        controls = tk.Frame(self.screen, bg=WHITE, padx=12, pady=10)
        controls.pack(fill="x")
        quantity_var = tk.StringVar(value="1")
        ttk.Label(controls, text="Количество:").pack(side="left")
        ttk.Entry(controls, textvariable=quantity_var, width=7).pack(side="left", padx=8)

        def select_row(event):
            if tree.selection():
                quantity_var.set(str(self.cart[int(tree.selection()[0])]["quantity"]))

        def change_quantity():
            stock_id = self.selected_id(tree)
            quantity = parse_quantity(quantity_var.get())
            item = self.cart[stock_id]
            product, sizes = service.product_details(item["product_id"])
            stock = next((row for row in sizes if row["stock_item_id"] == stock_id), None)
            if stock is None or quantity > stock["quantity_available"]:
                raise ValueError("Столько пар сейчас нет. Уменьшите количество или удалите позицию")
            item["quantity"] = quantity
            item["unit_price"] = product["sale_price"]
            self.show_cart()

        def remove_item():
            del self.cart[self.selected_id(tree)]
            self.show_cart()

        tree.bind("<<TreeviewSelect>>", select_row)
        ttk.Button(controls, text="Изменить", command=lambda: self.safe(change_quantity)).pack(side="left", padx=4)
        ttk.Button(controls, text="Удалить позицию", command=lambda: self.safe(remove_item)).pack(side="left", padx=4)
        ttk.Button(controls, text="Отказаться от заказа", command=self.cancel_cart).pack(side="right")
        ttk.Button(controls, text="Подтвердить заказ", style="Action.TButton", command=lambda: self.safe(self.confirm_cart)).pack(side="right", padx=8)

    def cancel_cart(self):
        if not self.cart or messagebox.askyesno("Отмена заказа", "Очистить незавершённую корзину?", parent=self):
            self.cart.clear()
            self.safe(self.show_catalog)

    def confirm_cart(self):
        if self.user is None:
            raise ValueError("Сначала войдите в систему")
        quantities = {stock_id: item["quantity"] for stock_id, item in self.cart.items()}
        order_id = service.create_order(self.user["user_id"], quantities)
        self.cart.clear()
        messagebox.showinfo("Заказ оформлен", f"Заказ №{order_id} сохранён", parent=self)
        if self.return_to_orders:
            self.return_to_orders = False
            self.show_orders()
        else:
            self.show_catalog()

    def show_orders(self):
        if self.module < 4 or self.user is None:
            raise ValueError("Работа с заказами доступна в модуле 4 менеджеру и администратору")
        orders = service.list_orders(self.user["user_id"])
        self.change_screen("orders", "Заказы")
        self.make_header("Заказы", self.show_catalog)
        tree = self.make_table(self.screen, [("id", "Номер", 90), ("date", "Дата", 140),
                               ("model", "ФИО клиента", 480), ("total", "Сумма", 160)])
        for order in orders:
            tree.insert("", "end", iid=str(order["order_id"]), values=(order["order_id"], order["order_date"].isoformat(), order["client_name"], money(order["total"])))
        controls = tk.Frame(self.screen, bg=WHITE, padx=12, pady=10)
        controls.pack(fill="x")

        def inspect():
            self.show_order_detail(self.selected_id(tree))

        def edit():
            self.show_order_detail(self.selected_id(tree), editing=True)

        def new_order():
            self.return_to_orders = True
            self.show_catalog()
            messagebox.showinfo("Новый заказ", "Выберите товары в каталоге, добавьте их в корзину и подтвердите заказ", parent=self)

        def delete():
            order_id = self.selected_id(tree)
            if messagebox.askyesno("Удаление заказа", f"Удалить заказ №{order_id} и вернуть его пары в доступное количество?", parent=self):
                service.delete_order(self.user["user_id"], order_id)
                messagebox.showinfo("Заказ удалён", "Заказ и его позиции удалены", parent=self)
                self.show_orders()

        ttk.Button(controls, text="Состав заказа", command=lambda: self.safe(inspect)).pack(side="left", padx=4)
        ttk.Button(controls, text="Новый заказ", style="Action.TButton", command=lambda: self.safe(new_order)).pack(side="left", padx=4)
        ttk.Button(controls, text="Удалить заказ", command=lambda: self.safe(delete)).pack(side="left", padx=4)
        if self.user["role_code"] == "admin":
            ttk.Button(controls, text="Редактировать", command=lambda: self.safe(edit)).pack(side="left", padx=4)
        tree.bind("<Double-1>", lambda event: self.safe(inspect))

    def show_order_detail(self, order_id, editing=False):
        if editing and (self.user is None or self.user["role_code"] != "admin"):
            raise ValueError("Редактировать заказ может только администратор")
        order, items = service.order_details(self.user["user_id"], order_id)
        self.change_screen("order_detail", "Редактирование заказа" if editing else "Состав заказа")
        self.make_header(f"Заказ №{order_id}", self.show_orders)
        ttk.Label(self.screen, text="Клиент: " + order["client_name"]).pack(anchor="w", padx=15, pady=8)
        date_var = tk.StringVar(value=order["order_date"].isoformat())
        date_row = tk.Frame(self.screen, bg=WHITE, padx=15)
        date_row.pack(fill="x")
        ttk.Label(date_row, text="Дата (ГГГГ-ММ-ДД):").pack(side="left", padx=(0, 8))
        if editing:
            ttk.Entry(date_row, textvariable=date_var, width=16).pack(side="left")
        else:
            ttk.Label(date_row, textvariable=date_var).pack(side="left")
        tree = self.make_table(self.screen, [("model", "Модель / производство", 470), ("size", "Размер", 90),
                               ("quantity", "Пар", 70), ("price", "Цена за пару", 130), ("total", "Сумма", 130)])
        total_label = ttk.Label(self.screen)
        total_label.pack(anchor="e", padx=15, pady=8)
        removed = set()

        def redraw():
            for iid in tree.get_children():
                tree.delete(iid)
            total = Decimal("0")
            for item in items:
                if item["order_item_id"] in removed:
                    continue
                line_total = item["quantity"] * item["unit_price"]
                total += line_total
                tree.insert("", "end", iid=str(item["order_item_id"]), values=(item["product_name"] + " / " + item["manufacturer"],
                            size_text(item["size_value"]), item["quantity"], money(item["unit_price"]), money(line_total)))
            total_label.configure(text="Итого: " + money(total))

        redraw()
        if editing:
            controls = tk.Frame(self.screen, bg=WHITE, padx=12, pady=10)
            controls.pack(fill="x")

            def remove():
                item_id = self.selected_id(tree)
                if len(removed) + 1 >= len(items):
                    raise ValueError("Не оставляйте заказ пустым. Для этого удалите весь заказ")
                removed.add(item_id)
                redraw()

            def save():
                if removed and not messagebox.askyesno("Сохранение заказа", "Удалить отмеченные позиции и сохранить изменения?", parent=self):
                    return
                service.edit_order(self.user["user_id"], order_id, date_var.get(), removed)
                messagebox.showinfo("Заказ сохранён", "Изменения сохранены", parent=self)
                self.show_orders()

            ttk.Button(controls, text="Удалить выбранную позицию", command=lambda: self.safe(remove)).pack(side="left", padx=4)
            ttk.Button(controls, text="Сохранить", style="Action.TButton", command=lambda: self.safe(save)).pack(side="right", padx=4)
            ttk.Button(controls, text="Отмена", command=lambda: self.safe(self.show_orders)).pack(side="right", padx=4)

    def close_app(self):
        if self.cart and not messagebox.askyesno("Выход", "Незавершённый заказ будет потерян. Закрыть приложение?", parent=self):
            return
        self.destroy()
