"""Все окна приложения. Здесь создаются виджеты и вызываются функции service."""

from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

import psycopg
from PIL import Image, ImageTk

from app import service
from app.common import money

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
    def __init__(self):
        super().__init__()
        self.user = None
        self.products = []
        self.current_screen = ""
        self.current_scroll = None
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
        self.result_label = ttk.Label(self.screen)
        self.result_label.pack(anchor="w", padx=14, pady=4)
        self.catalog_scroll = ScrollFrame(self.screen)
        self.catalog_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.current_scroll = self.catalog_scroll
        self.render_catalog()


    def render_catalog(self):
        for child in self.catalog_scroll.inner.winfo_children():
            child.destroy()
        rows = list(self.products)
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

            def resize_text(event, panel=info):
                for label in panel.winfo_children():
                    label.configure(wraplength=max(120, event.width))

            info.bind("<Configure>", resize_text)
            title = tk.Label(info, text=product["manufacturer"] + " | " + product["product_name"], bg=color,
                             font=("Calibri", 12, "bold"), anchor="w", justify="left", wraplength=560)
            title.pack(fill="x")
            for text in (product["category"], f"Количество: {product['total_quantity']}", "Состав: " + product["composition"]):
                tk.Label(info, text=text, bg=color, anchor="w", justify="left", wraplength=560).pack(fill="x", pady=2)
        self.catalog_scroll.canvas.yview_moveto(0)


    def scroll_wheel(self, event):
        if self.current_scroll is None:
            return
        if getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0:
            direction = -1
        else:
            direction = 1
        self.current_scroll.canvas.yview_scroll(direction, "units")











    def close_app(self):
        self.destroy()
