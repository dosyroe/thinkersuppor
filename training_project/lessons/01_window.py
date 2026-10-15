"""Первое упражнение: окно и кнопка. База данных не нужна."""

import tkinter as tk
from tkinter import ttk, messagebox


def say_hello():
    messagebox.showinfo("Кнопка работает", "Ты нажал кнопку. Это вызвало функцию say_hello.")


window = tk.Tk()
window.title("Чудо Обувь — Первое окно")
window.geometry("600x400")
window.minsize(400, 300)
window.configure(bg="white")

label = ttk.Label(window, text="Моё первое окно на Python", font=("Calibri", 18))
label.pack(pady=30)

button = ttk.Button(window, text="Нажми меня", command=say_hello)
button.pack(pady=10)

window.mainloop()
