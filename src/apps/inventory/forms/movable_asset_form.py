from django import forms

from apps.common.forms import widget_styles
from apps.inventory.models import AssetSpec, MovableAsset

_INPUT = widget_styles.INPUT
_SELECT = widget_styles.SELECT
_TEXTAREA = widget_styles.TEXTAREA


class MovableAssetForm(forms.ModelForm):
    class Meta:
        model = MovableAsset
        fields = [
            "code", "name", "description",
            "category", "sector", "location", "responsible", "ownership",
            "status", "condition", "notes",
        ]
        widgets = {
            "code":        forms.TextInput(attrs={"class": _INPUT, "placeholder": "Ex: PAT-0001", "autofocus": True}),
            "name":        forms.TextInput(attrs={"class": _INPUT, "placeholder": "Nome do item"}),
            "description": forms.Textarea(attrs={"class": _TEXTAREA, "rows": 3, "placeholder": "Descrição opcional"}),
            "category":    forms.Select(attrs={"class": _SELECT}),
            "sector":      forms.Select(attrs={"class": _SELECT}),
            "location":    forms.Select(attrs={"class": _SELECT}),
            "responsible": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Nome do responsável"}),
            "ownership":   forms.Select(attrs={"class": _SELECT}),
            "status":      forms.Select(attrs={"class": _SELECT}),
            "condition":   forms.Select(attrs={"class": _SELECT}),
            "notes":       forms.Textarea(attrs={"class": _TEXTAREA, "rows": 3, "placeholder": "Observações"}),
        }


class AssetSpecForm(forms.ModelForm):
    # brand is handled manually in the view (select existing or create new)
    new_brand_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": _INPUT,
            "placeholder": "Digite o nome da nova marca",
            "id": "new_brand_name_input",
            "autocomplete": "off",
        })
    )

    class Meta:
        model = AssetSpec
        fields = ["model_name", "serial_number", "image"]
        widgets = {
            "model_name":    forms.TextInput(attrs={"class": _INPUT, "placeholder": "Ex: Inspiron 15"}),
            "serial_number": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Número de série"}),
            "image":         forms.ClearableFileInput(attrs={"class": "hidden", "accept": "image/*"}),
        }
