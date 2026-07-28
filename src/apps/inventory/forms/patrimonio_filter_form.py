from django import forms
from django.utils.translation import gettext_lazy as _

from apps.common.forms import widget_styles
from apps.inventory.models import ItemCondition

_INPUT = widget_styles.INPUT
_SELECT = widget_styles.SELECT

TIPO_CHOICES = [
    ("", _("All")),
    ("movel", _("Item")),
    ("imovel", _("Real Estate")),
]


class PatrimonioFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": _("Code or name")}),
    )
    tipo = forms.ChoiceField(
        required=False,
        label=_("Type"),
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={"class": _SELECT}),
    )
    condition = forms.ChoiceField(
        required=False,
        label=_("Condition"),
        choices=[("", _("All"))] + list(ItemCondition.choices),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
