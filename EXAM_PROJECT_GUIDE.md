# Чудо Обувь: сборка проекта для экзамена

**Python + Tkinter/ttk + PostgreSQL + pgAdmin, школьная М ОС Linux.** Инструкция для модулей 1–4 КИМ 09.02.07-2. Отдельная учебная инструкция EXAM_LINUX_GUIDE.md сохранена без изменений.

Здесь полный код, который нужно написать, и действия по созданию проекта с нуля. Иди последовательно: база → каталог → оформление → управление заказами. Новые возможности добавляются в исходники, переключателя MODULE нет. Программа имеет один обычный запуск `python main.py`.

Окружение устанавливается одной командой pip. В проекте нет аналитики, pandas, учебных упражнений, программы диагностики, ORM и сервера API. Поиск, фильтр и сортировка доступны гостю и вошедшему пользователю: КИМ, страница 6, разрешает гостевой каталог без них, но не запрещает их наличие. Оформление и просмотр конкретной модели требуют входа. Заказы менеджера и администратора проверяются по роли. Справа сверху выводится ФИО; подпись роли по КИМ не обязательна.

Под «без лишних функций» здесь понимаются возможности приложения. Функции подключения, проверки ввода, сообщений и транзакций нужны, чтобы программа корректно выполняла задание. Возврат остатков при удалении заказа и защита от частичного сохранения сохранены.

Рядом находятся `exam_project` с итоговым кодом и `exam_versions` с реальными версиями после модулей 2, 3 и 4. Это пример для подготовки. На экзамене самостоятельно создаёшь описанные файлы и копируешь только официальные ресурсы, выданные организаторами; приносить готовый проект инструкция не предполагает.

Ваша договорённость: Автотеста на пробнике нет, проверка ожидается ручная. Его контрольные суммы не придумываются. Требования КИМ к функциям и результатам остаются; конкретное место передачи файлов задаёт преподаватель. КИМ требует последовательного выполнения 1–4, но не устанавливает запрет начать следующий модуль до немедленной отправки предыдущего.

## Как читать эту инструкцию

Команды bash выполняются в терминале Linux. SQL — в Query Tool pgAdmin. Код Python записывается в файлы `.py`. Сохраняй файлы в UTF-8, отступы Python — четыре пробела. Редактор должен запускать интерпретатор `.venv/bin/python`.

Для service.py и ui.py показаны полные версии после каждого этапа. Если создаёшь проект копированием при подготовке, **заменяй содержимое соответствующего файла целиком**, а не дописывай вторую копию класса внизу. Если пишешь сам, добавляй новые методы и обновляй нужные участки, сверяясь с полной версией. Каждая показанная версия запускается без методов будущего модуля.

## 0. Подготовить проект

PostgreSQL, pgAdmin и Python с Tkinter должны быть подготовлены на компьютере. Для Calibri заранее проверь наличие шрифта. Через pip Tkinter не устанавливается. Если в день подготовки эти компоненты отсутствуют, установка системных пакетов выполняется с преподавателем средствами М ОС; команды Ubuntu/apt здесь не предполагаются.

### 0.1. Папка и venv

В терминале открой рабочую папку:

```bash
mkdir chudo_obuv
cd chudo_obuv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install "psycopg[binary]" openpyxl Pillow
```

psycopg — подключение PostgreSQL; openpyxl — чтение XLSX; Pillow — изображения. После открытия нового терминала достаточно снова выполнить `source .venv/bin/activate`. Все дальнейшие команды запуска выполняются из корня chudo_obuv.

Создай requirements.txt со списком ниже. Для следующего компьютера используется `python -m pip install -r requirements.txt`; после установки выше повторять её не нужно.

### Файл `requirements.txt`

```text
psycopg[binary]
openpyxl
Pillow
```

### 0.2. Папки и официальные ресурсы

Через редактор или файловый менеджер создай `app`, `database`, `data`, `assets`, `assets/products`. В data помести пять XLSX из задания: Products_import.xlsx, Sizes_import.xlsx, Stock_Items_import.xlsx, Users_import.xlsx и Orders_import.xlsx.

31 фото из Images положи в assets/products под их исходными именами. Логотип «Чудо Обувь.png» скопируй как assets/logo.png; picture.png — как assets/picture.png; «Чудо Обувь.ico» — как assets/app.ico. Не искажай изображения и не меняй их цвета. На Linux регистр имён важен.

Итоговая структура:

```text
chudo_obuv/
    main.py
    settings.py
    import_data.py
    requirements.txt
    README.md
    .gitignore
    ERD_module_1.pdf
    app/
        __init__.py
        db.py
        common.py
        service.py
        ui.py
    database/
        schema.sql
        database_with_data.sql
    data/
        Products_import.xlsx
        Sizes_import.xlsx
        Stock_Items_import.xlsx
        Users_import.xlsx
        Orders_import.xlsx
    assets/
        logo.png
        picture.png
        app.ico
        products/
            IMG_...png
```

ERD и database_with_data.sql получаются при выполнении шагов ниже. Не нужно писать вручную сотни INSERT для данных: их загружает написанный importer, а экспорт сохраняет БД. `.venv` локальна и не входит в ZIP.

В готовом примере эти два результата уже включены: PDF соответствует приложенной структуре, SQL содержит первоначально импортированные данные и проверен восстановлением в отдельную PostgreSQL-базу. На экзамене получаешь их из своей работы по шагам ниже; после изменений базы экспорт обновляется.

### 0.3. Git

Если Git входит в вашу сдачу, создай .gitignore:

### Файл `.gitignore`

```text
.venv/
__pycache__/
*.pyc
*.zip
*.rar
```

В терминале:

```bash
git init
```

Если Git требует сведения автора, настрой реальные свои или выданные значения:

```bash
git config user.name "Имя Фамилия"
git config user.email "ТВОЙ_EMAIL"
```

После каждого законченного модуля выполняй `git add .` и `git commit -m "Module 1: database"`, меняя сообщение для следующего этапа. ZIP сохраняй вне репозитория; в Git нужны обычные исходники и ресурсы. Адрес удалённого репозитория и отправка — по выданной инструкции, случайный URL сюда не добавлен.

## 1. Модуль 1 — база и данные

Результат: нормализованная база с данными, ERD_module_1.pdf, SQL структуры с данными. Рекомендуемый КИМ ориентир — 50 минут.

### 1.1. Подключить сервер и создать базу в pgAdmin

1. Открой pgAdmin. Подключись к уже зарегистрированному серверу либо выбери Servers → Register → Server.
2. General → Name: любое понятное название. Connection: выданный Host, Port, Username и Password; Maintenance database — postgres. Для локального сервера обычный пример 127.0.0.1:5432, но используй реальные параметры.
3. В дереве сервера: Databases → Create → Database. Имя chudo_obuv; владелец — выданный пользователь PostgreSQL. Если организатор уже создал базу, используй её.
4. Выдели chudo_obuv, открой Query Tool. Выполни `SELECT current_database(), current_user;`: должна быть именно нужная база.

Пользователь PostgreSQL с паролем подключает программу к базе. Пользователь магазина вроде asidorova входит в приложение без пароля. Master password pgAdmin, если спрашивается, относится к настройкам pgAdmin.

### 1.2. Выбрать таблицы и связи

| Таблица | Что хранится | Важная связь |
| --- | --- | --- |
| roles | Роль | role_id у пользователя |
| users | ФИО и уникальный логин | role_id → roles |
| products | Модель, производство, категория, описание, состав, фото, базовая цена | product_id у товарной позиции |
| sizes | Значение размера, включая половинные | size_id у товарной позиции |
| stock_items | Конкретные модель+размер и остаток | product_id → products, size_id → sizes |
| orders | Дата и пользователь | user_id → users |
| order_items | Состав, количество, историческая цена | order_id → orders, stock_item_id → stock_items |

Все связи один ко многим. PK — уникальный идентификатор строки, FK — ссылка на строку другой таблицы. Размер и цена NUMERIC, количество INTEGER, дата DATE. Текст VARCHAR/TEXT. Нельзя хранить размер 36.5 как целое число. Сведения о модели не повторяются во всех заказах; сумма заказа вычисляется по составу. Историческая цена хранится в order_items.unit_price, независимо от текущей products.price.

### 1.3. Создать структуру

Запиши database/schema.sql, открой его в Query Tool нужной **пустой** базы и выполни целиком. BEGIN/COMMIT объединяют создание в транзакцию. NOT NULL — обязательное поле; UNIQUE — без повторов; CHECK — допустимое значение; REFERENCES — внешний ключ.

### Файл `database/schema.sql`

```sql
-- Выполнять один раз в новой пустой БД chudo_obuv через Query Tool pgAdmin.
-- Скрипт не создаёт сервер PostgreSQL, пользователя или саму базу данных.
BEGIN;

CREATE TABLE public.roles (
    role_id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    role_code VARCHAR(20) NOT NULL UNIQUE,
    role_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE public.users (
    user_id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100) NOT NULL,
    login VARCHAR(100) NOT NULL UNIQUE,
    role_id INTEGER NOT NULL REFERENCES public.roles(role_id)
);

CREATE TABLE public.products (
    product_id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    image_path VARCHAR(255),
    product_name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    composition TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    UNIQUE (product_name, manufacturer)
);

CREATE TABLE public.sizes (
    size_id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    size_value NUMERIC(4, 1) NOT NULL UNIQUE CHECK (size_value > 0)
);

CREATE TABLE public.stock_items (
    stock_item_id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES public.products(product_id),
    size_id INTEGER NOT NULL REFERENCES public.sizes(size_id),
    quantity_available INTEGER NOT NULL CHECK (quantity_available >= 0),
    UNIQUE (product_id, size_id)
);

CREATE TABLE public.orders (
    order_id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    order_date DATE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES public.users(user_id)
);

CREATE TABLE public.order_items (
    order_item_id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES public.orders(order_id) ON DELETE CASCADE,
    stock_item_id INTEGER NOT NULL REFERENCES public.stock_items(stock_item_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    UNIQUE (order_id, stock_item_id)
);

CREATE INDEX orders_order_date_idx ON public.orders(order_date);
CREATE INDEX order_items_stock_item_id_idx ON public.order_items(stock_item_id);

COMMIT;
```

При ошибке в транзакции сначала `ROLLBACK;`, затем исправление причины. Повторять CREATE в уже созданной базе не нужно. Для новой тренировки создай другую пустую базу.

### 1.4. Настройки и подключение Python

Создай следующие файлы. Параметры settings.py замени на выданные, включая пароль PostgreSQL. MODULE здесь нет.

### Файл `settings.py`

```python
DB_HOST = "127.0.0.1"
DB_PORT = 5432
DB_NAME = "chudo_obuv"
DB_USER = "postgres"
DB_PASSWORD = "ВПИШИ_ПАРОЛЬ_POSTGRESQL"
```

### Файл `app/__init__.py`

```python
"""Код учебного приложения Чудо Обувь."""
```

### Файл `app/db.py`

```python
import psycopg
from psycopg.rows import dict_row

import settings


def get_connection():
    return psycopg.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        connect_timeout=5,
        row_factory=dict_row,
    )
```

get_connection открывает PostgreSQL; dict_row даёт доступ к результату по имени столбца. Конструкция `with get_connection()` сохраняет изменения при успехе и откатывает при исключении, затем закрывает подключение. [Документация psycopg](https://www.psycopg.org/psycopg3/docs/basic/usage.html).

### 1.5. Написать и запустить импорт

Создай import_data.py в корне. Код читает пять официальных Excel из data, создаёт словари соответствия названий и ID и загружает таблицы в порядке внешних ключей. Все записи — одна транзакция.

### Файл `import_data.py`

```python
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from openpyxl import load_workbook
from app.db import get_connection
import psycopg

DATA_DIR = Path(__file__).resolve().parent / "data"


def clean(value):
    return " ".join(str(value).replace("\u00a0", " ").split())


def number(value):
    return Decimal(str(value).replace(",", "."))


def whole_number(value):
    number_value = number(value)
    if number_value != number_value.to_integral_value() or number_value < 0:
        raise ValueError(f"Ожидалось целое неотрицательное число: {value}")
    return int(number_value)


def model_key(name, manufacturer):
    name = clean(name)
    manufacturer = clean(manufacturer)
    if name == "Черные туфли в классическом стиле" and manufacturer == "Барбари":
        name = "Черные туфли в классическом стиле — база для деловых образов"
    return name, manufacturer


def read_excel(filename):
    book = load_workbook(DATA_DIR / filename, read_only=True, data_only=True)
    try:
        return [row for row in book.worksheets[0].iter_rows(min_row=2, values_only=True)
                if any(value is not None for value in row)]
    finally:
        book.close()


def insert_id(cursor, query, values):
    cursor.execute(query, values)
    return next(iter(cursor.fetchone().values()))


def import_data():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM roles")
            if cursor.fetchone()["total"] != 0:
                raise ValueError("Импорт рассчитан на новую пустую базу")

            roles = {}
            for code, name in [("admin", "Администратор"),
                               ("manager", "Менеджер"),
                               ("customer", "Авторизованный пользователь")]:
                roles[name] = insert_id(cursor,
                    "INSERT INTO roles (role_code, role_name) VALUES (%s, %s) RETURNING role_id",
                    (code, name))

            products = {}
            for category, subcategory, image, name, manufacturer, description, composition, price in read_excel("Products_import.xlsx"):
                key = model_key(name, manufacturer)
                if key in products:
                    raise ValueError(f"Повтор модели: {key}")
                products[key] = insert_id(cursor,
                    """INSERT INTO products
                       (category, subcategory, image_path, product_name, manufacturer,
                        description, composition, price)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING product_id""",
                    (clean(category), clean(subcategory), image, key[0], key[1],
                     description or "", composition or "", number(price)))

            sizes = {}
            for row in read_excel("Sizes_import.xlsx"):
                value = number(row[0])
                sizes[value] = insert_id(cursor,
                    "INSERT INTO sizes (size_value) VALUES (%s) RETURNING size_id", (value,))

            users = {}
            for last_name, first_name, middle_name, login, role in read_excel("Users_import.xlsx"):
                fio = " ".join(clean(value) for value in (last_name, first_name, middle_name))
                if fio in users:
                    raise ValueError(f"Неоднозначное ФИО: {fio}")
                users[fio] = insert_id(cursor,
                    """INSERT INTO users (last_name, first_name, middle_name, login, role_id)
                       VALUES (%s, %s, %s, %s, %s) RETURNING user_id""",
                    (clean(last_name), clean(first_name), clean(middle_name), clean(login), roles[clean(role)]))

            stock_items = {}
            for name, manufacturer, size, quantity in read_excel("Stock_Items_import.xlsx"):
                key = (products[model_key(name, manufacturer)], sizes[number(size)])
                stock_items[key] = insert_id(cursor,
                    """INSERT INTO stock_items (product_id, size_id, quantity_available)
                       VALUES (%s, %s, %s) RETURNING stock_item_id""", (*key, whole_number(quantity)))

            orders = {}
            for order_id, order_date, fio, category, name, manufacturer, size, quantity, price in read_excel("Orders_import.xlsx"):
                order_id = int(order_id)
                if isinstance(order_date, datetime):
                    order_date = order_date.date()
                user_id = users[clean(fio)]
                if order_id not in orders:
                    cursor.execute("INSERT INTO orders (order_id, order_date, user_id) VALUES (%s, %s, %s)",
                                   (order_id, order_date, user_id))
                    orders[order_id] = (order_date, user_id)
                elif orders[order_id] != (order_date, user_id):
                    raise ValueError(f"Разные клиент/дата у заказа {order_id}")
                key = (products[model_key(name, manufacturer)], sizes[number(size)])
                cursor.execute("""INSERT INTO order_items (order_id, stock_item_id, quantity, unit_price)
                                  VALUES (%s, %s, %s, %s)""",
                               (order_id, stock_items[key], whole_number(quantity), number(price)))

            cursor.execute("""SELECT setval(pg_get_serial_sequence('public.orders', 'order_id'),
                              COALESCE(MAX(order_id), 1), COUNT(*) > 0) FROM orders""")
    print("Импорт завершён")


if __name__ == "__main__":
    try:
        import_data()
    except (ValueError, KeyError, OSError, psycopg.Error) as error:
        raise SystemExit(f"Импорт не выполнен: {error}") from error
```

Запуск:

```bash
python import_data.py
```

Ожидается «Импорт завершён». Повторный импорт в заполненную базу запрещён, чтобы не дублировать записи.

clean исправляет лишние и неразрывные пробелы. model_key сопоставляет укороченное название «Черные туфли в классическом стиле» производителя Барбари с полным названием в Products. Изменять все похожие имена по догадке нельзя. Размеры преобразуются Decimal. Таблицы читаются по порядку столбцов, поэтому опечатка заголовка отчества не ломает импорт. ФИО «Пeтр» сохраняется как в исходнике.

Исторические заказы НЕ списываются из выданных доступных остатков повторно. 30 строк Orders — это состав 10 заказов, а не 30 разных заказов. setval в конце сдвигает генератор номера после старых заказов 1–10. Название модели сопоставляется вместе с производителем, а не по описанию.

Значения SQL передаются отдельно от текста через `%s`; `(value,)` — кортеж одного значения. Не используй f-string для подстановки пользовательского логина в SQL. [Параметры psycopg](https://www.psycopg.org/psycopg3/docs/basic/params.html).

### 1.6. Проверить данные в Query Tool

Выполни:

```sql
SELECT 'roles' AS entity, COUNT(*) AS actual, 3 AS expected FROM roles
UNION ALL SELECT 'users', COUNT(*), 20 FROM users
UNION ALL SELECT 'products', COUNT(*), 31 FROM products
UNION ALL SELECT 'sizes', COUNT(*), 35 FROM sizes
UNION ALL SELECT 'stock_items', COUNT(*), 92 FROM stock_items
UNION ALL SELECT 'orders', COUNT(*), 10 FROM orders
UNION ALL SELECT 'order_items', COUNT(*), 30 FROM order_items;

SELECT SUM(quantity_available) AS available_pairs FROM stock_items;
SELECT SUM(quantity) AS historical_pairs FROM order_items;

SELECT u.login, r.role_name
FROM users u JOIN roles r ON r.role_id = u.role_id;
```

Ожидается 1274 доступные пары и 36 исторически заказанных пар. Контрольные количества относятся к исходному состоянию до новых заказов. SELECT читает данные, JOIN соединяет связанные таблицы, SUM складывает значения.

### 1.7. Создать ERD_module_1.pdf

В pgAdmin выбери schema public или базу → Generate ERD, если функция доступна в установленной версии. Проверь семь таблиц, поля, PK/FK и связи:

```text
roles → users → orders → order_items
products → stock_items → order_items
sizes → stock_items
```

Расположи таблицы без перекрытия, включи отображение столбцов и скачай схему через Download image. В LibreOffice Draw открой изображение, выбери альбомную страницу, размести диаграмму целиком и экспортируй File → Export As → Export as PDF. Название ERD_module_1.pdf. Проверь, что текст читается и все края видны. Если ERD Tool отсутствует, нарисуй те же таблицы/связи в доступном редакторе и экспортируй PDF. [Документация ERD Tool](https://www.pgadmin.org/docs/pgadmin4/latest/erd_tool.html).

Простое переименование картинки в PDF не создаёт PDF. Редактируемую диаграмму полезно сохранить отдельно; схема сдачи должна совпадать с созданной БД.

### 1.8. Экспорт структуры с данными

В терминале из корня проекта, подставив свои параметры:

```bash
pg_dump -h 127.0.0.1 -p 5432 -U postgres -d chudo_obuv --no-owner --no-privileges --inserts -f database/database_with_data.sql
```

Альтернатива в pgAdmin: база → Backup; Filename database/database_with_data.sql; Format Plain; Pre-data, Data, Post-data включены; Only data и Only schemas выключены; Do not save Owner/Privileges включены; Use INSERT commands включён. Дождись успешного завершения. Наименования вкладок в школьной версии могут отличаться. [Документация Backup](https://www.pgadmin.org/docs/pgadmin4/latest/backup_dialog.html).

Перед следующим этапом: база заполнена, ERD и SQL сохранены, результаты модуля переданы в согласованное место, коммит сделан. Автотест и контрольные суммы на вашем пробнике не требуются по договорённости.

## 2. Модуль 2 — каталог

Результат: каталог из БД, скидка, стиль и запускаемый Module_2_Catalog.zip. Ориентир КИМ — 40 минут. Пока входа и корзины нет: они появятся при разработке следующего этапа.

### 2.1. Общие расчёты и каталог из базы

Создай app/common.py и app/service.py по версиям модуля 2. Скидка 25% означает цену ×0.75. Границы прошлого календарного месяца — первый день прошлого месяца включительно и первый день текущего не включительно. Например, при расчёте в октябре проверяется сентябрь, а не последние 30 дней. При январе учитывается декабрь прошлого года.

### Файл `app/common.py` — версия после модуля 2

```python
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP


def month_bounds(reference_date):
    """Предыдущий календарный месяц, включая переход январь → декабрь."""
    current_month = reference_date.replace(day=1)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)
    return previous_month, current_month

def price_with_discount(price, has_previous_orders):
    multiplier = Decimal("1") if has_previous_orders else Decimal("0.75")
    return (price * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def money(value):
    return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " ₽"
```

### Файл `app/service.py` — версия после модуля 2

```python
from datetime import date

from app.common import month_bounds, price_with_discount
from app.db import get_connection


def load_catalog(reference_date=None):
    previous_month, current_month = month_bounds(reference_date or date.today())
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """WITH totals AS (
                       SELECT product_id, SUM(quantity_available) AS total_quantity
                       FROM stock_items GROUP BY product_id
                   )
                   SELECT p.*, COALESCE(t.total_quantity, 0) AS total_quantity,
                          EXISTS (
                              SELECT 1 FROM order_items i
                              JOIN stock_items s ON s.stock_item_id = i.stock_item_id
                              JOIN orders o ON o.order_id = i.order_id
                              WHERE s.product_id = p.product_id
                                AND o.order_date >= %s AND o.order_date < %s
                          ) AS has_previous_orders
                   FROM products p LEFT JOIN totals t ON t.product_id = p.product_id
                   ORDER BY p.product_id""",
                (previous_month, current_month),
            )
            products = cursor.fetchall()
    for product in products:
        product["sale_price"] = price_with_discount(product["price"], product["has_previous_orders"])
    return products
```

load_catalog складывает остатки всех размеров одной модели, проверяет EXISTS хотя бы одного заказа прошлого месяца и добавляет sale_price. Products.price не изменяется. LEFT JOIN сохраняет модель даже без остатков; COALESCE даёт 0.

### 2.2. Создать интерфейс каталога

Создай app/ui.py. Ниже полностью запускаемая версия модуля 2. ScrollFrame содержит Canvas + внутренний Frame + Scrollbar. Карточки помещаются во внутренний Frame; события Configure пересчитывают область прокрутки и ширину.

### Файл `app/ui.py` — версия после модуля 2

```python
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
```

В render_catalog для каждой модели создаются изображение, производство/название, категория, количество, состав и фактическая цена. При суммарном остатке ≤3 весь фон карточки #ff8080. Основной фон #FFFFFF, дополнительный #D2F6E7, акцент #70B2AF, шрифт Calibri. picture применяет thumbnail без изменения пропорций и при отсутствии фото открывает picture.png. Ссылка label.image сохраняет картинку для Tkinter.

safe показывает ошибки пользователю; сообщения не заменяются голым traceback. Все страницы имеют заголовок. Настройка iconphoto использует выданный ICO через Pillow, что не требует Windows iconbitmap. Прокрутка обработана для Windows и Linux.

### 2.3. Запуск

Создай main.py:

### Файл `main.py`

```python
from app.ui import ShoeApp


if __name__ == "__main__":
    application = ShoeApp()
    application.mainloop()
```

В терминале:

```bash
python main.py
```

Должно быть 31 модель, логотип, фото, прокрутка и три красные карточки в исходных данных. «Черный кофе» — 3 пары, «Туфли из натуральной кожи» Берестов — 3, «Ботинки мужские демисезонные» Барбари — 2. Окно растягивается. С исходными апрельскими/майскими заказами при расчёте в октябре у всех моделей будет скидка: за сентябрь покупок нет.

### 2.4. Сохранить модуль 2

Создай краткий README.md с названием, технологиями, назначением каталога, шагами подготовки базы и командой запуска; полный итоговый текст дан в 4.3. Сохрани исходники, настройки, ресурсы, ERD и SQL с данными. Через файловый менеджер упакуй выбранные файлы в **Module_2_Catalog.zip**, за пределами проекта. .venv, __pycache__, .git исключи. Сделай коммит.

2.2 КИМ — понятная структура, 2.3 — стиль именования. Функции/переменные snake_case, классы PascalCase. Этот проект разделяет запуск, БД, операции и интерфейс. Комментарии объясняют неочевидные места.

## 3. Модуль 3 — вход и оформление

Результат: вход по логину, ФИО, поиск/категория/сортировка, просмотр модели, корзина, подтверждение и Module_3_Interface.zip. Ориентир — 60 минут.

### 3.1. Дополнить common.py и service.py

Заменяй файлы на полные версии ниже. В common.py добавились проверка количества и вывод размера; старые расчёты сохранены. В service.py добавились require_user, login, product_details и create_order.

### Файл `app/common.py` — версия после модуля 3

```python
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP


def parse_quantity(value):
    """Количество пар должно быть положительным целым числом."""
    if isinstance(value, bool):
        raise ValueError("Количество должно быть положительным целым числом")
    try:
        quantity = int(str(value).strip())
    except (ValueError, TypeError) as error:
        raise ValueError("Введите целое количество пар, например 1 или 2") from error
    if quantity <= 0:
        raise ValueError("Количество должно быть больше нуля")
    return quantity


def month_bounds(reference_date):
    """Предыдущий календарный месяц, включая переход январь → декабрь."""
    current_month = reference_date.replace(day=1)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)
    return previous_month, current_month


def price_with_discount(price, has_previous_orders):
    multiplier = Decimal("1") if has_previous_orders else Decimal("0.75")
    return (price * multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def money(value):
    return f"{value:,.2f}".replace(",", " ").replace(".", ",") + " ₽"


def size_text(value):
    text = format(Decimal(str(value)), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text
```

### Файл `app/service.py` — версия после модуля 3

```python
"""Запросы к базе и операции с заказами. Tkinter в этом файле не нужен."""

from datetime import date

from app.common import month_bounds, parse_quantity, price_with_discount
from app.db import get_connection


def require_user(cursor, user_id, allowed_roles=None):
    cursor.execute(
        """SELECT u.user_id, u.last_name, u.first_name, u.middle_name, r.role_code
           FROM users u JOIN roles r ON r.role_id = u.role_id
           WHERE u.user_id = %s""",
        (user_id,),
    )
    user = cursor.fetchone()
    if user is None:
        raise ValueError("Сначала войдите в систему")
    if allowed_roles is not None and user["role_code"] not in allowed_roles:
        raise ValueError("Для вашей роли это действие недоступно")
    return user


def login(login_text):
    login_text = login_text.strip()
    if not login_text:
        raise ValueError("Введите логин")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT u.user_id, u.last_name, u.first_name, u.middle_name, r.role_code
                   FROM users u JOIN roles r ON r.role_id = u.role_id
                   WHERE u.login = %s""",
                (login_text,),
            )
            user = cursor.fetchone()
    if user is None:
        raise ValueError("Пользователь не найден. Проверьте введённый логин")
    return user


def load_catalog(reference_date=None):
    previous_month, current_month = month_bounds(reference_date or date.today())
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """WITH totals AS (
                       SELECT product_id, SUM(quantity_available) AS total_quantity
                       FROM stock_items GROUP BY product_id
                   )
                   SELECT p.*, COALESCE(t.total_quantity, 0) AS total_quantity,
                          EXISTS (
                              SELECT 1 FROM order_items i
                              JOIN stock_items s ON s.stock_item_id = i.stock_item_id
                              JOIN orders o ON o.order_id = i.order_id
                              WHERE s.product_id = p.product_id
                                AND o.order_date >= %s AND o.order_date < %s
                          ) AS has_previous_orders
                   FROM products p LEFT JOIN totals t ON t.product_id = p.product_id
                   ORDER BY p.product_id""",
                (previous_month, current_month),
            )
            products = cursor.fetchall()
    for product in products:
        product["sale_price"] = price_with_discount(product["price"], product["has_previous_orders"])
    return products


def product_details(product_id):
    product = next((row for row in load_catalog() if row["product_id"] == product_id), None)
    if product is None:
        raise ValueError("Модель не найдена. Обновите каталог")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT s.stock_item_id, s.quantity_available, z.size_value
                   FROM stock_items s JOIN sizes z ON z.size_id = s.size_id
                   WHERE s.product_id = %s ORDER BY z.size_value""",
                (product_id,),
            )
            sizes = cursor.fetchall()
    return product, sizes


def create_order(user_id, cart, order_date=None):
    if not cart:
        raise ValueError("Заказ пуст. Добавьте хотя бы одну позицию")
    quantities = {int(stock_id): parse_quantity(quantity) for stock_id, quantity in cart.items()}
    order_date = order_date or date.today()
    previous_month, current_month = month_bounds(order_date)
    prepared = []
    # Шапка, позиции и остатки сохраняются одной транзакцией.
    with get_connection() as connection:
        with connection.cursor() as cursor:
            require_user(cursor, user_id)
            # Одинаковый порядок блокировок снижает риск взаимной блокировки.
            for stock_id, quantity in sorted(quantities.items()):
                cursor.execute(
                    """SELECT s.stock_item_id, s.product_id, s.quantity_available,
                              p.product_name, p.price
                       FROM stock_items s JOIN products p ON p.product_id = s.product_id
                       WHERE s.stock_item_id = %s FOR UPDATE OF s""",
                    (stock_id,),
                )
                stock = cursor.fetchone()
                if stock is None:
                    raise ValueError("Товарная позиция больше не существует")
                if quantity > stock["quantity_available"]:
                    raise ValueError(f"{stock['product_name']}: осталось {stock['quantity_available']} пар. Уменьшите количество")
                cursor.execute(
                    """SELECT EXISTS (
                           SELECT 1 FROM order_items i
                           JOIN stock_items s ON s.stock_item_id = i.stock_item_id
                           JOIN orders o ON o.order_id = i.order_id
                           WHERE s.product_id = %s
                             AND o.order_date >= %s AND o.order_date < %s
                       ) AS has_orders""",
                    (stock["product_id"], previous_month, current_month),
                )
                price = price_with_discount(stock["price"], cursor.fetchone()["has_orders"])
                prepared.append((stock_id, quantity, price))
            cursor.execute(
                "INSERT INTO orders (order_date, user_id) VALUES (%s, %s) RETURNING order_id",
                (order_date, user_id),
            )
            order_id = cursor.fetchone()["order_id"]
            for stock_id, quantity, price in prepared:
                cursor.execute(
                    """INSERT INTO order_items (order_id, stock_item_id, quantity, unit_price)
                       VALUES (%s, %s, %s, %s)""",
                    (order_id, stock_id, quantity, price),
                )
                cursor.execute(
                    "UPDATE stock_items SET quantity_available = quantity_available - %s WHERE stock_item_id = %s",
                    (quantity, stock_id),
                )
    return order_id
```

login выполняет SELECT пользователя и роли по логину. Пустой/неизвестный логин вызывает понятную ошибку. Пароля магазина нет. product_details заново читает модель и размеры. Количество должно быть положительным целым числом; предел — остаток выбранного размера.

create_order проверяет пользователя и все количества, блокирует строки остатков FOR UPDATE, заново проверяет остаток и фактическую цену, добавляет шапку и позиции с unit_price, уменьшает остатки. Всё выполняется одним with/транзакцией. При ошибке сохранения ничего не остаётся наполовину. Новые номера назначает PostgreSQL через IDENTITY и RETURNING, не MAX+1.

### 3.2. Дополнить интерфейс

Замени app/ui.py на версию модуля 3. Это полная реализация вместе с прежним каталогом. После ввода логина ФИО справа, названия страниц меняются, «Назад» возвращает к предыдущему экрану.

### Файл `app/ui.py` — версия после модуля 3

```python
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
    def __init__(self):
        super().__init__()
        self.user = None
        self.cart = {}
        self.products = []
        self.current_screen = ""
        self.current_scroll = None
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
        if self.user is None:
            ttk.Button(toolbar, text="Войти", style="Action.TButton", command=self.show_login).pack(side="right")
        else:
            ttk.Button(toolbar, text="Выйти", command=self.logout).pack(side="right")
            ttk.Button(toolbar, text=f"Корзина ({sum(item['quantity'] for item in self.cart.values())})", style="Action.TButton", command=self.show_cart).pack(side="right", padx=8)
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

    def catalog_changed(self, *args):
        if self.current_screen == "catalog" and hasattr(self, "catalog_scroll"):
            self.render_catalog()

    def render_catalog(self):
        for child in self.catalog_scroll.inner.winfo_children():
            child.destroy()
        rows = list(self.products)
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

            def resize_text(event, panel=info):
                for label in panel.winfo_children():
                    label.configure(wraplength=max(120, event.width))

            info.bind("<Configure>", resize_text)
            title = tk.Label(info, text=product["manufacturer"] + " | " + product["product_name"], bg=color,
                             font=("Calibri", 12, "bold"), anchor="w", justify="left", wraplength=560)
            title.pack(fill="x")
            for text in (product["category"], f"Количество: {product['total_quantity']}", "Состав: " + product["composition"]):
                tk.Label(info, text=text, bg=color, anchor="w", justify="left", wraplength=560).pack(fill="x", pady=2)
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
        self.safe(self.show_catalog)

    def show_product(self, product_id):
        if self.user is None:
            raise ValueError("Для просмотра модели и оформления заказа войдите по логину")
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
        self.show_catalog()



    def close_app(self):
        if self.cart and not messagebox.askyesno("Выход", "Незавершённый заказ будет потерян. Закрыть приложение?", parent=self):
            return
        self.destroy()
```

main.py и settings.py остаются теми же: `python main.py` запускает текущую написанную версию.

### 3.3. Проверить вход, поиск и просмотр

Войди asidorova. В исходнике это клиент; papetrov — менеджер, isivanov — администратор. Список логинов можно прочитать SELECT из users. Проверь неверный логин и повторный выход/вход.

render_catalog сначала применяет категорию и строку поиска, затем сортирует sale_price. Поиск casefold: название ИЛИ описание, без регистра. StringVar хранит выбранные параметры. trace_add вызывает обновление при вводе; Combobox — при выборе. «Все категории» снимает фильтр категории, текущий поиск и направление сохраняются. Кнопки «Найти» нет. Эти элементы доступны и гостю, что допустимо по КИМ и не требует проверки роли для поиска.

Клик по модели после входа показывает актуальные сведения из БД, весь её размерный ряд и доступные размеры с остатком >0. Гостю при попытке перейти показывается сообщение о необходимости входа. Выбранная позиция корзины идентифицируется stock_item_id: два размера одной модели — разные строки.

### 3.4. Проверить корзину и запись заказа

Добавь две разные модели/размера; повторное добавление той же позиции должно увеличить её количество. Проверь 0, -1, дробь, буквы и превышение остатка: сообщение без закрытия. Измени количество, удали строку, откажись от заказа. До подтверждения меняется только словарь корзины, БД не списывается.

Подтверди новый заказ. Корзина очищается после успеха, каталог перечитывается. В pgAdmin:

```sql
SELECT * FROM orders ORDER BY order_id DESC;
SELECT * FROM order_items ORDER BY order_item_id DESC;
```

Проверь пользователя, дату, позиции, количество и unit_price. Номер нового заказа больше 10. Остаток уменьшился на правильное число пар выбранного размера; старые unit_price не зависят от изменения цены модели. Отменённая корзина не создаёт шапку.

### 3.5. Сохранить модуль 3

Обнови описание функций README, выгрузи актуальную БД с данными, сохрани **Module_3_Interface.zip** и коммит. По 3.2 покажи сообщения ошибки/предупреждения/информации, по 3.3 — обработку неверного ввода и БД, по 3.4 — комментарии сложных операций.

## 4. Модуль 4 — управление заказами и итоговый проект

Результат: менеджер/администратор управляют заказами, только админ редактирует, итоговые README/SQL/ERD/исходники и Module_4_Orders.zip. Ориентир — 60 минут.

### 4.1. Дополнить SQL-операции

Замени app/service.py на полный итоговый вариант. В нём появились list_orders, order_details, delete_order и edit_order. Роль проверяется внутри операций, а не только наличием кнопки. common.py, импорт, структура и настройки не меняются.

### Файл `app/service.py` — версия после модуля 4

```python
"""Запросы к базе и операции с заказами. Tkinter в этом файле не нужен."""

from datetime import date

from app.common import month_bounds, parse_quantity, price_with_discount
from app.db import get_connection


def require_user(cursor, user_id, allowed_roles=None):
    cursor.execute(
        """SELECT u.user_id, u.last_name, u.first_name, u.middle_name, r.role_code
           FROM users u JOIN roles r ON r.role_id = u.role_id
           WHERE u.user_id = %s""",
        (user_id,),
    )
    user = cursor.fetchone()
    if user is None:
        raise ValueError("Сначала войдите в систему")
    if allowed_roles is not None and user["role_code"] not in allowed_roles:
        raise ValueError("Для вашей роли это действие недоступно")
    return user


def login(login_text):
    login_text = login_text.strip()
    if not login_text:
        raise ValueError("Введите логин")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT u.user_id, u.last_name, u.first_name, u.middle_name, r.role_code
                   FROM users u JOIN roles r ON r.role_id = u.role_id
                   WHERE u.login = %s""",
                (login_text,),
            )
            user = cursor.fetchone()
    if user is None:
        raise ValueError("Пользователь не найден. Проверьте введённый логин")
    return user


def load_catalog(reference_date=None):
    previous_month, current_month = month_bounds(reference_date or date.today())
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """WITH totals AS (
                       SELECT product_id, SUM(quantity_available) AS total_quantity
                       FROM stock_items GROUP BY product_id
                   )
                   SELECT p.*, COALESCE(t.total_quantity, 0) AS total_quantity,
                          EXISTS (
                              SELECT 1 FROM order_items i
                              JOIN stock_items s ON s.stock_item_id = i.stock_item_id
                              JOIN orders o ON o.order_id = i.order_id
                              WHERE s.product_id = p.product_id
                                AND o.order_date >= %s AND o.order_date < %s
                          ) AS has_previous_orders
                   FROM products p LEFT JOIN totals t ON t.product_id = p.product_id
                   ORDER BY p.product_id""",
                (previous_month, current_month),
            )
            products = cursor.fetchall()
    for product in products:
        product["sale_price"] = price_with_discount(product["price"], product["has_previous_orders"])
    return products


def product_details(product_id):
    product = next((row for row in load_catalog() if row["product_id"] == product_id), None)
    if product is None:
        raise ValueError("Модель не найдена. Обновите каталог")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT s.stock_item_id, s.quantity_available, z.size_value
                   FROM stock_items s JOIN sizes z ON z.size_id = s.size_id
                   WHERE s.product_id = %s ORDER BY z.size_value""",
                (product_id,),
            )
            sizes = cursor.fetchall()
    return product, sizes


def create_order(user_id, cart, order_date=None):
    if not cart:
        raise ValueError("Заказ пуст. Добавьте хотя бы одну позицию")
    quantities = {int(stock_id): parse_quantity(quantity) for stock_id, quantity in cart.items()}
    order_date = order_date or date.today()
    previous_month, current_month = month_bounds(order_date)
    prepared = []
    # Шапка, позиции и остатки сохраняются одной транзакцией.
    with get_connection() as connection:
        with connection.cursor() as cursor:
            require_user(cursor, user_id)
            # Одинаковый порядок блокировок снижает риск взаимной блокировки.
            for stock_id, quantity in sorted(quantities.items()):
                cursor.execute(
                    """SELECT s.stock_item_id, s.product_id, s.quantity_available,
                              p.product_name, p.price
                       FROM stock_items s JOIN products p ON p.product_id = s.product_id
                       WHERE s.stock_item_id = %s FOR UPDATE OF s""",
                    (stock_id,),
                )
                stock = cursor.fetchone()
                if stock is None:
                    raise ValueError("Товарная позиция больше не существует")
                if quantity > stock["quantity_available"]:
                    raise ValueError(f"{stock['product_name']}: осталось {stock['quantity_available']} пар. Уменьшите количество")
                cursor.execute(
                    """SELECT EXISTS (
                           SELECT 1 FROM order_items i
                           JOIN stock_items s ON s.stock_item_id = i.stock_item_id
                           JOIN orders o ON o.order_id = i.order_id
                           WHERE s.product_id = %s
                             AND o.order_date >= %s AND o.order_date < %s
                       ) AS has_orders""",
                    (stock["product_id"], previous_month, current_month),
                )
                price = price_with_discount(stock["price"], cursor.fetchone()["has_orders"])
                prepared.append((stock_id, quantity, price))
            cursor.execute(
                "INSERT INTO orders (order_date, user_id) VALUES (%s, %s) RETURNING order_id",
                (order_date, user_id),
            )
            order_id = cursor.fetchone()["order_id"]
            for stock_id, quantity, price in prepared:
                cursor.execute(
                    """INSERT INTO order_items (order_id, stock_item_id, quantity, unit_price)
                       VALUES (%s, %s, %s, %s)""",
                    (order_id, stock_id, quantity, price),
                )
                cursor.execute(
                    "UPDATE stock_items SET quantity_available = quantity_available - %s WHERE stock_item_id = %s",
                    (quantity, stock_id),
                )
    return order_id


def list_orders(user_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            require_user(cursor, user_id, {"manager", "admin"})
            cursor.execute(
                """SELECT o.order_id, o.order_date,
                          u.last_name || ' ' || u.first_name || ' ' || u.middle_name AS client_name,
                          COALESCE(SUM(i.quantity * i.unit_price), 0) AS total
                   FROM orders o JOIN users u ON u.user_id = o.user_id
                   LEFT JOIN order_items i ON i.order_id = o.order_id
                   GROUP BY o.order_id, o.order_date, u.last_name, u.first_name, u.middle_name
                   ORDER BY o.order_date DESC, o.order_id DESC"""
            )
            return cursor.fetchall()


def order_details(user_id, order_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            require_user(cursor, user_id, {"manager", "admin"})
            cursor.execute(
                """SELECT o.order_id, o.order_date,
                          u.last_name || ' ' || u.first_name || ' ' || u.middle_name AS client_name
                   FROM orders o JOIN users u ON u.user_id = o.user_id WHERE o.order_id = %s""",
                (order_id,),
            )
            order = cursor.fetchone()
            if order is None:
                raise ValueError("Заказ уже удалён. Обновите список")
            cursor.execute(
                """SELECT i.order_item_id, i.stock_item_id, i.quantity, i.unit_price,
                          p.product_name, p.manufacturer, z.size_value
                   FROM order_items i JOIN stock_items s ON s.stock_item_id = i.stock_item_id
                   JOIN products p ON p.product_id = s.product_id
                   JOIN sizes z ON z.size_id = s.size_id
                   WHERE i.order_id = %s ORDER BY i.order_item_id""",
                (order_id,),
            )
            return order, cursor.fetchall()


def delete_order(user_id, order_id):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            require_user(cursor, user_id, {"manager", "admin"})
            cursor.execute("SELECT order_id FROM orders WHERE order_id = %s FOR UPDATE", (order_id,))
            if cursor.fetchone() is None:
                raise ValueError("Заказ уже удалён. Обновите список")
            cursor.execute("SELECT stock_item_id, quantity FROM order_items WHERE order_id = %s ORDER BY stock_item_id", (order_id,))
            items = cursor.fetchall()
            # Возврат остатков и удаление заказа выполняются вместе.
            for item in items:
                cursor.execute("UPDATE stock_items SET quantity_available = quantity_available + %s WHERE stock_item_id = %s", (item["quantity"], item["stock_item_id"]))
            cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))


def edit_order(user_id, order_id, date_text, removed_ids):
    try:
        new_date = date.fromisoformat(date_text.strip())
    except ValueError as error:
        raise ValueError("Введите существующую дату в формате ГГГГ-ММ-ДД, например 2026-10-13") from error
    if new_date.isoformat() != date_text.strip():
        raise ValueError("Формат даты: ГГГГ-ММ-ДД")
    removed_ids = {int(item_id) for item_id in removed_ids}
    with get_connection() as connection:
        with connection.cursor() as cursor:
            require_user(cursor, user_id, {"admin"})
            cursor.execute("SELECT order_id FROM orders WHERE order_id = %s FOR UPDATE", (order_id,))
            if cursor.fetchone() is None:
                raise ValueError("Заказ уже удалён. Обновите список")
            cursor.execute("SELECT order_item_id, stock_item_id, quantity FROM order_items WHERE order_id = %s ORDER BY stock_item_id", (order_id,))
            items = cursor.fetchall()
            existing_ids = {item["order_item_id"] for item in items}
            if not removed_ids <= existing_ids:
                raise ValueError("Состав заказа изменился. Откройте его заново")
            if removed_ids and removed_ids == existing_ids:
                raise ValueError("Нельзя сохранить пустой заказ. Удалите его целиком в списке заказов")
            for item in items:
                if item["order_item_id"] in removed_ids:
                    cursor.execute("UPDATE stock_items SET quantity_available = quantity_available + %s WHERE stock_item_id = %s", (item["quantity"], item["stock_item_id"]))
                    cursor.execute("DELETE FROM order_items WHERE order_item_id = %s AND order_id = %s", (item["order_item_id"], order_id))
            cursor.execute("UPDATE orders SET order_date = %s WHERE order_id = %s", (new_date, order_id))
```

list_orders показывает дату, ФИО и итог по сохранённым ценам. order_details читает состав с моделью/производством, размером, количеством, unit_price и суммами. delete_order после проверки роли возвращает пары, удаляет шапку и состав одной транзакцией. ON DELETE CASCADE удаляет строки, но возврат остатка сделан отдельно — сам каскад этого не делает.

edit_order доступен только admin. Проверяет настоящую дату ГГГГ-ММ-ДД и принадлежность удаляемых строк выбранному заказу; возвращает их количество и изменяет дату в одной транзакции. Нельзя сохранить пустой заказ: для этого есть удаление целого заказа. Это выбранное поведение неопределённого в КИМ случая последней строки.

### 4.2. Дополнить интерфейс

Замени app/ui.py на полный итоговый вариант. После входа менеджером/админом появляется «Заказы». Остальным общий список не предоставляется.

### Файл `app/ui.py` — версия после модуля 4

```python
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
    def __init__(self):
        super().__init__()
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

    def catalog_changed(self, *args):
        if self.current_screen == "catalog" and hasattr(self, "catalog_scroll"):
            self.render_catalog()

    def render_catalog(self):
        for child in self.catalog_scroll.inner.winfo_children():
            child.destroy()
        rows = list(self.products)
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

            def resize_text(event, panel=info):
                for label in panel.winfo_children():
                    label.configure(wraplength=max(120, event.width))

            info.bind("<Configure>", resize_text)
            title = tk.Label(info, text=product["manufacturer"] + " | " + product["product_name"], bg=color,
                             font=("Calibri", 12, "bold"), anchor="w", justify="left", wraplength=560)
            title.pack(fill="x")
            for text in (product["category"], f"Количество: {product['total_quantity']}", "Состав: " + product["composition"]):
                tk.Label(info, text=text, bg=color, anchor="w", justify="left", wraplength=560).pack(fill="x", pady=2)
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
        if self.user is None:
            raise ValueError("Для просмотра модели и оформления заказа войдите по логину")
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
        if self.user is None:
            raise ValueError("Работа с заказами доступна менеджеру и администратору после входа")
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
```

show_orders создаёт список, просмотр состава, новый заказ и удаление. Новый заказ использует уже написанные каталог и корзину и связывается с вошедшим пользователем; отдельный выбор другого клиента в ТЗ не задан. Перед удалением askyesno: «Нет» — ничего не меняется; «Да» — транзакция, сообщение и обновлённый список.

Только администратор видит редактирование. Дата и полный состав загружаются из БД при открытии. Удаление строк сначала отмечается локально; до «Сохранить» БД не меняется. «Отмена» возвращает к списку без сохранения. После записи список обновляется автоматически; при возврате в каталог остатки перечитываются.

### 4.3. Итоговый README.md

Запиши полный текст ниже в корень проекта. На своей сдаче укажи реальные выполненные функции и доступный способ восстановления; не обещай реализованные возможности, если они ещё не написаны.

### Файл `README.md`

````markdown
# Чудо Обувь — оформление заказов

Python, Tkinter/ttk, PostgreSQL. Администрирование базы — pgAdmin.

Приложение показывает каталог обуви с фотографиями, доступным количеством и ценой со скидкой. Поиск по названию и описанию, фильтр категории и сортировка цены работают совместно в реальном времени и доступны гостю. Вход выполняется только по логину. После входа можно выбирать модель, размер и количество, редактировать корзину, отменять и подтверждать заказ. Менеджер и администратор просматривают, добавляют и удаляют заказы. Администратор также меняет дату и удаляет отдельные позиции.

Цена покупки сохраняется в составе заказа. Оформление и изменения заказов пересчитывают остатки одной транзакцией. В каталоге суммируются остатки всех размеров модели; количество ≤3 подсвечивается. Скидка 25% применяется, когда модель не заказывали в предыдущем календарном месяце.

## Подготовка и запуск на Linux

Нужны установленный Python с Tkinter, работающий PostgreSQL и данные подключения к нему.

В терминале из корня проекта:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

В `settings.py` укажи host, port, название базы, пользователя PostgreSQL и пароль. Указанные `postgres` и `5432` — пример; используй выданные данные. В IDE выбери `.venv/bin/python`.

Выбери **один** способ подготовки базы.

### Создать начальную базу из Excel

1. В pgAdmin создай пустую базу `chudo_obuv`.
2. Открой Query Tool этой базы и выполни `database/schema.sql`.
3. В терминале выполни `python import_data.py` один раз. Пять исходных Excel находятся в `data`.

### Восстановить сохранённое состояние

Создай пустую базу в pgAdmin. Если передан `database/database_with_data.sql`, восстанови её, подставив свои параметры:

```bash
psql -h 127.0.0.1 -p 5432 -U postgres -d chudo_obuv -v ON_ERROR_STOP=1 -f database/database_with_data.sql
```

После восстановления дампа schema.sql и import_data.py повторно не запускаются. Пароль PostgreSQL вводится по запросу. Дамп сохраняет состояние на момент экспорта; исходные Excel не содержат позднейших заказов.

В этом комплекте уже есть SQL с исходными импортированными данными и PDF схемы. После создания или изменения заказов перед своей сдачей обнови SQL экспортом из своей базы.

### Запуск приложения

```bash
python main.py
```

При повторном запуске активируй окружение и выполни эту команду. В приложении пароля нет по заданию. Логины исходных пользователей: `asidorova` — клиент, `papetrov` — менеджер, `isivanov` — администратор.

## Файлы проекта

- `main.py` — запуск.
- `settings.py` — подключение PostgreSQL.
- `app/db.py` — подключение к базе.
- `app/common.py` — количества, деньги, размеры и даты скидки.
- `app/service.py` — SQL и операции заказов.
- `app/ui.py` — интерфейс.
- `import_data.py` — импорт официальных Excel.
- `database/schema.sql` — структура БД.
- `database/database_with_data.sql` — сохранённая структура с данными, создаётся экспортом.
- `ERD_module_1.pdf` — схема, создаётся при выполнении модуля 1.
- `data` и `assets` — официальные Excel и изображения.

## Сохранение текущей базы

```bash
pg_dump -h 127.0.0.1 -p 5432 -U postgres -d chudo_obuv --no-owner --no-privileges --inserts -f database/database_with_data.sql
```

Вместо этой команды можно использовать Backup в pgAdmin: Plain, схема и данные, Use INSERT commands, без владельцев и прав. Перед сдачей экспорт обновляется. Исходники и ресурсы передаются вместе с README, ERD и актуальным SQL с данными. `.venv` и `__pycache__` в архив не включаются.

Имена файлов на Linux чувствительны к регистру. Tkinter и Calibri должны быть доступны в школьной ОС. Если Tkinter отсутствует в системном Python, его устанавливают средствами ОС в день подготовки, через pip он не устанавливается.
````

### 4.4. Экспорт и проверка восстановления

Снова выполни экспорт из 1.8 после своих изменений. schema.sql содержит только структуру, а исходные Excel только первоначальные записи. database_with_data.sql должен сохранять текущую БД.

Для проверки создай в pgAdmin другую пустую базу chudo_restore. В терминале:

```bash
psql -h 127.0.0.1 -p 5432 -U postgres -d chudo_restore -v ON_ERROR_STOP=1 -f database/database_with_data.sql
```

Поменяй только DB_NAME в settings.py на chudo_restore и запусти main.py. После восстановления дампа schema.sql и importer повторно не нужны. Команда psql читает и SQL, и служебные команды из вывода pg_dump. Если используешь сгенерированный без служебных команд INSERT-скрипт, его можно выполнить целиком через Query Tool пустой базы.

### 4.5. Состав сдачи

В репозитории обычными файлами должны находиться исходники, конфигурация, ресурсы, ERD_module_1.pdf, скрипт БД с данными и README.md в корне UTF-8 Markdown. Коммить изменения и отправляй в предоставленный репозиторий по процедуре преподавателя. Архив не заменяет исходники в Git.

Файлы результатов: **ERD_module_1.pdf**, **Module_2_Catalog.zip**, **Module_3_Interface.zip**, **Module_4_Orders.zip**. При создании ZIP выбирай исходники, настройки, assets/data/database, README и ERD; исключай .venv, __pycache__, .git. Сохраняй снимок каждого этапа, позднейший исходник не подменяет уже сохранённый ранний этап.

На странице 25 КИМ в общем составе результатов упоминаются исполняемые файлы, но отдельный формат сборки Python-приложения не указан. Эта инструкция задаёт воспроизводимый запуск исходников `python main.py`; требование отдельного собранного файла зависит от уточнения организаторов. `.dt` относится к 1С. Не считай один исполняемый файл заменой исходников и БД.

Точные правила ручной передачи на вашем пробнике не описаны в КИМ. Соблюдай выданную процедуру; контрольные суммы Автотеста не подставляй случайными строками.

## 5. Финальная ручная сверка модулей 1–4

| Проверка | Ожидается |
| --- | --- |
| Структура и импорт | 7 таблиц, PK/FK, правильные исходные количества, половинные размеры |
| ERD и SQL | PDF соответствует базе; SQL восстанавливает структуру и данные |
| Гость | Каталог, изображения, цвета, скидки; поиск/фильтр/сортировка работают |
| Вход | Только логин, ФИО справа на страницах, понятная ошибка неправильного логина |
| Поиск | Название ИЛИ описание, без регистра; совместно с категорией и выбранной сортировкой |
| Модель | Актуальные сведения, размерный ряд, только доступные для покупки размеры |
| Корзина | Несколько позиций, изменение/удаление/отказ; до подтверждения БД не меняется |
| Подтверждение | Пользователь/дата/цены/позиции сохранены, остатки списаны, каталог обновлён |
| Менеджер | Список, состав, добавление, удаление; отмена удаления не меняет БД |
| Администратор | Дополнительно дата и удаление отдельных строк; отмена редактирования не сохраняет |
| Удаление | Возврат пар и удаление атомарны, повторное удаление не возвращает пары дважды |
| Файлы | README, SQL с данными, ERD, ресурсы, точные ZIP; исходники обычными файлами в Git |

## 6. Быстро найти причину ошибки

| Сообщение | Действие |
| --- | --- |
| No module named psycopg/openpyxl/PIL | Активировать правильный venv и установить три библиотеки |
| Нет tkinter/_tkinter | Подготовить системный компонент Tkinter в М ОС с преподавателем |
| connection refused / authentication failed | Проверить то же подключение в pgAdmin и параметры settings.py |
| relation does not exist | Проверить имя БД и выполнить schema.sql в правильной пустой базе |
| already exists | Не повторять создание таблиц в готовой базе |
| current transaction is aborted | ROLLBACK, исправить первую SQL-ошибку, повторить действие |
| Импорт в непустую базу | Не импортировать повторно; для репетиции создать новую пустую базу |
| FileNotFoundError | Проверить папку, регистр и точные имена официальных файлов |
| IndentationError/SyntaxError | Сверить отступы, кавычки, скобки и двоеточия с полной версией |
| Всё со скидкой | Проверить прошлый календарный месяц: октябрь с данными апреля/мая даёт скидку всем |

Учебная версия сохранена отдельно. В экзаменационном проекте один запуск, без режимов, без учебных упражнений и аналитических зависимостей. Проверку на школьной М ОС выполняй в день подготовки: наличие Tkinter/Calibri и выданные параметры PostgreSQL зависят от компьютера.

