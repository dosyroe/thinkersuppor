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
