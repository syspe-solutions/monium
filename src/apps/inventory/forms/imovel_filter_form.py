from django import forms
from django.utils.translation import gettext_lazy as _

from apps.common.forms import widget_styles
from apps.inventory.models import CartorioSituacao, ImovelCategory, ZonaTipo

_INPUT = widget_styles.INPUT
_SELECT = widget_styles.SELECT


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
