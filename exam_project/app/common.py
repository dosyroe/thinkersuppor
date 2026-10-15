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
