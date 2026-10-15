"""Модуль 5: шаблон для CSV, которых пока нет в исходном комплекте.

Сначала сверь реальные столбцы и настрой COLUMN_MAPS.
Слева — имя, которое использует код; справа — настоящее имя столбца CSV.
Неизвестные имена в настройках ниже являются примером, а не описанием
отсутствующих исходных файлов.
"""

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "analytics_data"
CSV_SEPARATOR = ","  # Если поля в выданных CSV разделены ;, поставь ";".
CSV_ENCODING = "utf-8-sig"
DATE_FORMAT = "ISO8601"  # Пример: 2026-01-03 или 2026-01-03 12:30:00.
START = pd.Timestamp("2026-01-01")
END = pd.Timestamp("2026-04-01")  # Верхняя граница не включается.

COLUMN_MAPS = {
    "sessions": {
        "session_id": "session_id", "user_id": "user_id",
        "started_at": "started_at", "device_type": "device_type",
        "traffic_source": "traffic_source",
    },
    "orders": {
        "order_id": "order_id", "user_id": "user_id",
        "session_id": "session_id", "ordered_at": "ordered_at",
        "status": "status", "discount_percent": "discount_percent",
    },
    "items": {
        "order_id": "order_id", "model_id": "model_id",
        "quantity": "quantity", "unit_price": "unit_price",
        "line_total": "line_total", "discount_percent": "discount_percent",
    },
    "models": {"model_id": "model_id", "category": "category"},
}

# Выбери по структуре настоящих CSV. Не угадывай по отсутствующим данным.
# "orders": скидка у заказа, количество суммируем до уровня заказа.
# "items": скидка и количество даны в строках позиций.
DISCOUNT_LEVEL = "orders"

# "quantity_times_unit_price": unit_price — итоговая цена за пару.
# "line_total": в CSV уже есть итоговая стоимость целой строки.
# Если цена исходная, до скидки, сначала нужна формула по описанию CSV.
LINE_AMOUNT = "quantity_times_unit_price"


def read_table(kind, filename, required):
    path = DATA_DIR / filename
    if not path.is_file():
        raise ValueError(f"Нет {path.name}. Нужны четыре CSV приложения 4 в analytics_data")
    table = pd.read_csv(path, sep=CSV_SEPARATOR, encoding=CSV_ENCODING, dtype=str)
    mapping = COLUMN_MAPS[kind]
    missing = [mapping[name] for name in required if mapping[name] not in table.columns]
    if missing:
        raise ValueError(f"{filename}: нет столбцов {missing}. Реальные столбцы: {list(table.columns)}. Исправь COLUMN_MAPS")
    return table.rename(columns={mapping[name]: name for name in required})[required].copy()


def unique_key(table, column, name):
    if table[column].isna().any() or table[column].duplicated().any():
        raise ValueError(f"{name}: {column} должен быть заполненным уникальным идентификатором")


def numeric(table, column):
    table[column] = pd.to_numeric(table[column].str.replace(",", ".", regex=False), errors="raise")
    if table[column].isna().any():
        raise ValueError(f"Пустое число в {column}")


def date_column(table, column):
    table[column] = pd.to_datetime(table[column], format=DATE_FORMAT, errors="raise")
    if table[column].isna().any():
        raise ValueError(f"Пустая дата в {column}")


def winners(series):
    if series.empty or series.dropna().empty:
        return "Нет данных"
    maximum = series.max()
    # При равенстве показываем всех: КИМ не задаёт правило выбора одного.
    return ", ".join(str(value) for value in series.index[series == maximum])


def calculate():
    if DISCOUNT_LEVEL not in ("orders", "items"):
        raise ValueError("DISCOUNT_LEVEL должен быть orders или items")
    if LINE_AMOUNT not in ("quantity_times_unit_price", "line_total"):
        raise ValueError("Проверь LINE_AMOUNT")
    order_columns = ["order_id", "user_id", "session_id", "ordered_at", "status"]
    if DISCOUNT_LEVEL == "orders":
        order_columns.append("discount_percent")
    item_columns = ["order_id", "model_id", "quantity"]
    item_columns.append("unit_price" if LINE_AMOUNT == "quantity_times_unit_price" else "line_total")
    if DISCOUNT_LEVEL == "items":
        item_columns.append("discount_percent")

    sessions = read_table("sessions", "Sessions_analytics.csv",
                          ["session_id", "user_id", "started_at", "device_type", "traffic_source"])
    orders = read_table("orders", "Orders_analytics.csv", order_columns)
    items = read_table("items", "Order_items_analytics.csv", item_columns)
    models = read_table("models", "Shoe_models_analytics.csv", ["model_id", "category"])
    for table, column, name in [(sessions, "session_id", "sessions"),
                                (orders, "order_id", "orders"), (models, "model_id", "models")]:
        unique_key(table, column, name)
    for table, column in [(sessions, "user_id"), (orders, "user_id"), (orders, "session_id"),
                          (items, "order_id"), (items, "model_id"), (sessions, "device_type"),
                          (sessions, "traffic_source"), (models, "category")]:
        if table[column].isna().any():
            raise ValueError(f"Есть пустые значения в {column}; проверь CSV")
    date_column(sessions, "started_at")
    date_column(orders, "ordered_at")
    numeric(items, "quantity")
    if ((items["quantity"] <= 0) | (items["quantity"] % 1 != 0)).any():
        raise ValueError("quantity должно содержать целое положительное число пар")
    amount_column = "unit_price" if LINE_AMOUNT == "quantity_times_unit_price" else "line_total"
    numeric(items, amount_column)
    if (items[amount_column] < 0).any():
        raise ValueError("Стоимость не может быть отрицательной")
    discount_table = orders if DISCOUNT_LEVEL == "orders" else items
    numeric(discount_table, "discount_percent")
    if not discount_table["discount_percent"].between(0, 100).all():
        raise ValueError("В этом шаблоне скидка задана в процентах от 0 до 100")
    if not items["order_id"].isin(orders["order_id"]).all():
        raise ValueError("Есть позиции без соответствующего заказа")
    if not items["model_id"].isin(models["model_id"]).all():
        raise ValueError("Есть позиции без соответствующей модели")

    visits = sessions.loc[(sessions["started_at"] >= START) & (sessions["started_at"] < END)].copy()
    completed = orders.loc[(orders["status"].str.strip().str.casefold() == "completed")
                           & (orders["ordered_at"] >= START) & (orders["ordered_at"] < END)].copy()
    lines = items.merge(completed[["order_id"]], on="order_id", how="inner", validate="many_to_one")
    if visits.empty or completed.empty:
        raise ValueError("В периоде нет посещений или completed-заказов")
    if not completed["order_id"].isin(lines["order_id"]).all():
        raise ValueError("Есть completed-заказ без позиций")

    # 5.1: один пользователь считается один раз внутри каждого устройства.
    purchases = completed.merge(sessions[["session_id", "user_id", "device_type"]], on="session_id",
                                 how="left", suffixes=("", "_session"), validate="many_to_one")
    if purchases["device_type"].isna().any() or (purchases["user_id"] != purchases["user_id_session"]).any():
        raise ValueError("Не найден тип устройства покупки либо пользователь заказа не совпадает с пользователем сессии")
    visitors = visits.groupby("device_type")["user_id"].nunique()
    buyers = purchases.groupby("device_type")["user_id"].nunique()
    if not buyers.index.isin(visitors.index).all():
        raise ValueError("Для устройства покупки нет посещений в выбранном периоде; сверь правило периода")
    conversion = buyers.reindex(visitors.index, fill_value=0) / visitors

    # 5.2: первая сессия и первая покупка, затем фильтр <= 7 суток, затем медиана.
    first_visits = visits.groupby("user_id")["started_at"].min()
    first_orders = completed.groupby("user_id")["ordered_at"].min()
    minutes = (first_orders - first_visits).dt.total_seconds() / 60
    eligible_minutes = minutes.loc[minutes.between(0, 7 * 24 * 60)]
    median = eligible_minutes.median()

    # 5.3: январская когорта и источник первого визита. При одинаковом
    # времени порядок первой сессии здесь определяется строковым session_id.
    first = visits.sort_values(["started_at", "session_id"]).drop_duplicates("user_id")
    january = first.loc[(first["started_at"] >= START) & (first["started_at"] < pd.Timestamp("2026-02-01"))].copy()
    february_users = set(visits.loc[(visits["started_at"] >= pd.Timestamp("2026-02-01"))
                                  & (visits["started_at"] < pd.Timestamp("2026-03-01")), "user_id"])
    january["returned"] = january["user_id"].isin(february_users)
    retention = january.groupby("traffic_source")["returned"].mean()

    # 5.4: сначала целая сумма заказа, потом квартили по суммам заказов.
    lines["amount"] = lines["quantity"] * lines["unit_price"] if LINE_AMOUNT == "quantity_times_unit_price" else lines["line_total"]
    totals = lines.groupby("order_id")["amount"].sum()
    q1, q3 = totals.quantile([0.25, 0.75], interpolation="linear")
    iqr = q3 - q1
    remaining = int(totals.between(q1 - 1.5 * iqr, q3 + 1.5 * iqr).sum())

    # 5.5: один заказ получает один вес, если скидка дана у заказа.
    if DISCOUNT_LEVEL == "orders":
        quantities = lines.groupby("order_id")["quantity"].sum().rename("quantity")
        correlation_data = completed[["order_id", "discount_percent"]].merge(quantities, on="order_id", validate="one_to_one")
    else:
        correlation_data = lines[["discount_percent", "quantity"]]
    if len(correlation_data) < 2 or correlation_data["discount_percent"].nunique() < 2 or correlation_data["quantity"].nunique() < 2:
        correlation_answer = "Не определена: мало данных или одна переменная постоянна"
    else:
        correlation = correlation_data["discount_percent"].corr(correlation_data["quantity"], method="pearson")
        correlation_answer = f"{correlation:.3f}"

    # 5.6: сумма пар по категории, а не число строк заказа.
    category_lines = lines.merge(models, on="model_id", how="left", validate="many_to_one")
    sold = category_lines.groupby("category")["quantity"].sum()

    print("Конверсия по устройствам:\n", conversion.to_string())
    print("Удержание по источникам:\n", retention.to_string())
    print("Проданные пары по категориям:\n", sold.to_string())
    answers = {
        "5.1": winners(conversion),
        "5.2": float(median) if pd.notna(median) else "Нет пользователей, купивших за 7 суток",
        "5.3": winners(retention), "5.4": remaining,
        "5.5": correlation_answer, "5.6": winners(sold),
    }
    for task, answer in answers.items():
        print(f"{task}: {answer}")
    return answers


if __name__ == "__main__":
    try:
        calculate()
    except (ValueError, OSError, KeyError, pd.errors.ParserError) as error:
        raise SystemExit(f"Расчёт остановлен: {error}") from error
