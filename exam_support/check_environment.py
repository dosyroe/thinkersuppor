"""Read-only проверка Python, зависимостей, Tcl/Tk и доступности Calibri."""

import importlib
import platform
import sys


def main():
    print(f"Python: {sys.version.split()[0]}")
    print(f"Интерпретатор: {sys.executable}")
    print(f"Архитектура: {platform.machine()}")
    print(f"venv активен: {sys.prefix != sys.base_prefix}")
    failed = False
    for name in ("psycopg", "openpyxl", "PIL"):
        try:
            module = importlib.import_module(name)
            print(f"{name}: OK, {getattr(module, '__version__', 'версия не объявлена')}")
        except ImportError as error:
            failed = True
            print(f"{name}: ОШИБКА — {error}")
    try:
        import tkinter as tk
        import tkinter.font as tkfont
    except ImportError as error:
        print(f"Системный Tk: ОШИБКА — {error}")
        raise SystemExit(1) from error
    try:
        root = tk.Tk()
        root.withdraw()
        print(f"Tcl/Tk: {root.tk.call('info', 'patchlevel')}")
        available = {name.casefold() for name in tkfont.families(root)}
        print(f"Calibri в списке Tk: {'ДА' if 'calibri' in available else 'НЕТ — уточни у организатора'}")
        root.destroy()
    except tk.TclError as error:
        failed = True
        print(f"Графический Tk: ОШИБКА — {error}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
