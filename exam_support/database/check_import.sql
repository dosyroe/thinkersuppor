-- Контрольные значения относятся к начальному импорту, до тренировочных заказов.
SELECT 'roles' AS entity, COUNT(*) AS actual, 3 AS expected FROM public.roles
UNION ALL SELECT 'users', COUNT(*), 20 FROM public.users
UNION ALL SELECT 'products', COUNT(*), 31 FROM public.products
UNION ALL SELECT 'sizes', COUNT(*), 35 FROM public.sizes
UNION ALL SELECT 'stock_items', COUNT(*), 92 FROM public.stock_items
UNION ALL SELECT 'orders', COUNT(*), 10 FROM public.orders
UNION ALL SELECT 'order_items', COUNT(*), 30 FROM public.order_items;

SELECT SUM(quantity_available) AS available_pairs_expected_1274
FROM public.stock_items;

SELECT SUM(quantity) AS ordered_pairs_expected_36
FROM public.order_items;

SELECT p.product_name, p.manufacturer, SUM(s.quantity_available) AS available_pairs
FROM public.products AS p
JOIN public.stock_items AS s ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.manufacturer
HAVING SUM(s.quantity_available) <= 3
ORDER BY p.product_id;

SELECT o.order_id, o.order_date,
       u.last_name || ' ' || u.first_name || ' ' || u.middle_name AS client_name,
       COUNT(i.order_item_id) AS line_count,
       SUM(i.quantity * i.unit_price) AS order_total
FROM public.orders AS o
JOIN public.users AS u ON u.user_id = o.user_id
JOIN public.order_items AS i ON i.order_id = o.order_id
GROUP BY o.order_id, o.order_date, u.last_name, u.first_name, u.middle_name
ORDER BY o.order_id;

-- Значение последовательности orders после импорта должно учитывать номер 10.
SELECT pg_get_serial_sequence('public.orders', 'order_id') AS orders_sequence;

-- Сведения для сверки ERD и фактической схемы.
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
