from django import forms
from django.utils.translation import gettext_lazy as _

from apps.inventory.models import CartorioSituacao, ImovelCategory, ZonaTipo

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_SELECT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white focus:outline-none focus:ring-2 focus:ring-zinc-600"


class ImovelFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": _("Code, name or address")}),
    )
    category = forms.ModelChoiceField(
        required=False,
        label=_("Category"),
        queryset=ImovelCategory.objects.order_by("name"),
        empty_label=_("All"),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
    zone = forms.ChoiceField(
        required=False,
        label=_("Zone"),
        choices=[("", _("All"))] + list(ZonaTipo.choices),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
    cartorio_situacao = forms.ChoiceField(
        required=False,
        label=_("Registry status"),
        choices=[("", _("All"))] + list(CartorioSituacao.choices),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
