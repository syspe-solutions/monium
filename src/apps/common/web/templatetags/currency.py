from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def brl(value):
    if value in (None, ""):
        return "0,00"

    try:
        value = Decimal(value)
    except (InvalidOperation, TypeError):
        return value

    value = f"{value:,.2f}"
    value = value.replace(",", "X")
    value = value.replace(".", ",")
    value = value.replace("X", ".")

    return f"{value}"