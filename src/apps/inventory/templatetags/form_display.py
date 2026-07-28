from django import template
from django.forms import BoundField

register = template.Library()


@register.filter
def bound_field_display(field: BoundField) -> str:
    """Retorna o texto legível do valor atual de um campo do form: o rótulo
    da opção selecionada para campos de escolha, ou o valor bruto para
    campos de texto livre (ex.: busca)."""
    value = field.value()
    if not value:
        return ""
    choices = dict(getattr(field.field, "choices", []))
    return str(choices.get(value, value))
