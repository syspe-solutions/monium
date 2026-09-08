from django import forms
from django.utils.translation import gettext_lazy as _

from apps.common.forms import widget_styles
from apps.inventory.models import AssetStatus, Brand, Category, ItemCondition, Sector

_INPUT = widget_styles.INPUT
_SELECT = widget_styles.SELECT


class MovableAssetFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": _("Code, name or responsible")}),
    )
    status = forms.ChoiceField(
        required=False,
        label=_("Status"),
        choices=[("", _("All"))] + list(AssetStatus.choices),
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
