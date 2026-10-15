"""Второе упражнение: прокрутка и карточки. Список здесь учебный, без БД."""

import tkinter as tk
from tkinter import ttk

window = tk.Tk()
window.title("Чудо Обувь — Учебные карточки")
window.geometry("850x550")
window.minsize(650, 400)
window.configure(bg="white")

header = tk.Frame(window, bg="#D2F6E7", padx=15, pady=15)
header.pack(fill="x")
tk.Label(header, text="Чудо Обувь", bg="#D2F6E7", font=("Calibri", 20)).pack(side="left")

area = tk.Frame(window, bg="white")
area.pack(fill="both", expand=True)

canvas = tk.Canvas(area, bg="white", highlightthickness=0)
scrollbar = ttk.Scrollbar(area, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

cards_frame = tk.Frame(canvas, bg="white")
window_id = canvas.create_window((0, 0), window=cards_frame, anchor="nw")


def update_scroll(event):
    canvas.configure(scrollregion=canvas.bbox("all"))


def update_width(event):
    canvas.itemconfigure(window_id, width=event.width)


cards_frame.bind("<Configure>", update_scroll)
canvas.bind("<Configure>", update_width)

# Повторяем десять карточек только для упражнения с прокруткой.
for number in range(1, 11):
    color = "#ff8080" if number == 1 else "white"
    card = tk.Frame(cards_frame, bg=color, bd=1, relief="solid", padx=12, pady=12)
    card.pack(fill="x", padx=12, pady=6)
    tk.Label(card, text="Фото", bg="#D2F6E7", width=12, height=5).pack(side="left", padx=10)
    tk.Label(card, text=f"Модель №{number}\nКатегория: Женская обувь\nКоличество: {number}\nСостав: кожа",
             bg=color, justify="left", font=("Calibri", 12)).pack(side="left", padx=10)
    tk.Label(card, text="5 000 ₽", bg=color, font=("Calibri", 16)).pack(side="right", padx=15)

window.mainloop()
