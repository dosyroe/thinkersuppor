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
