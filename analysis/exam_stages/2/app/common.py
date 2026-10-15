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
