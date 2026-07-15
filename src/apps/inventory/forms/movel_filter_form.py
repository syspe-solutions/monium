from django import forms
from django.utils.translation import gettext_lazy as _

from apps.inventory.models import Brand, Category, ItemCondition, MovelStatus, Sector

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_SELECT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white focus:outline-none focus:ring-2 focus:ring-zinc-600"


class MovelFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": _("Code, name or responsible")}),
    )
    status = forms.ChoiceField(
        required=False,
        label=_("Status"),
        choices=[("", _("All"))] + list(MovelStatus.choices),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
    condition = forms.ChoiceField(
        required=False,
        label=_("Condition"),
        choices=[("", _("All"))] + list(ItemCondition.choices),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
    category = forms.ModelChoiceField(
        required=False,
        label=_("Category"),
        queryset=Category.objects.order_by("name"),
        empty_label=_("All"),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
    sector = forms.ModelChoiceField(
        required=False,
        label=_("Sector"),
        queryset=Sector.objects.order_by("name"),
        empty_label=_("All"),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
    brand = forms.ModelChoiceField(
        required=False,
        label=_("Brand"),
        queryset=Brand.objects.order_by("name"),
        empty_label=_("All"),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
