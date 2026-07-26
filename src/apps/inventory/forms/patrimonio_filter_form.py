from django import forms
from django.utils.translation import gettext_lazy as _

from apps.inventory.models import ItemCondition

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_SELECT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white focus:outline-none focus:ring-2 focus:ring-zinc-600"

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
