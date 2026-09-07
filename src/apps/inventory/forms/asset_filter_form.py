from django import forms
from django.utils.translation import gettext_lazy as _

from apps.common.forms import widget_styles
from apps.inventory.models import ItemCondition

_INPUT = widget_styles.INPUT
_SELECT = widget_styles.SELECT

ASSET_TYPE_CHOICES = [
    ("", _("All")),
    ("movable_asset", _("Item")),
    ("real_estate", _("Real Estate")),
]


class AssetFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={"class": _INPUT, "placeholder": _("Code or name")}),
    )
    asset_type = forms.ChoiceField(
        required=False,
        label=_("Type"),
        choices=ASSET_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": _SELECT}),
    )
    condition = forms.ChoiceField(
        required=False,
        label=_("Condition"),
        choices=[("", _("All"))] + list(ItemCondition.choices),
        widget=forms.Select(attrs={"class": _SELECT}),
    )
