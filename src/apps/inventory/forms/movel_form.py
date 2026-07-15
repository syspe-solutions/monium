from django import forms

from apps.inventory.models import Movel, MovelSpec

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_SELECT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white focus:outline-none focus:ring-2 focus:ring-zinc-600"
_TEXTAREA = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600 resize-none"


class MovelForm(forms.ModelForm):
    class Meta:
        model = Movel
        fields = [
            "code", "name", "description",
            "category", "sector", "location", "responsible", "ownership",
            "status", "condition", "notes",
        ]
        widgets = {
            "code":        forms.TextInput(attrs={"class": _INPUT, "placeholder": "Ex: PAT-0001"}),
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


class MovelSpecForm(forms.ModelForm):
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
        model = MovelSpec
        fields = ["model_name", "serial_number", "image"]
        widgets = {
            "model_name":    forms.TextInput(attrs={"class": _INPUT, "placeholder": "Ex: Inspiron 15"}),
            "serial_number": forms.TextInput(attrs={"class": _INPUT, "placeholder": "Número de série"}),
            "image":         forms.ClearableFileInput(attrs={"class": "text-sm text-zinc-500 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-sm file:font-medium file:bg-zinc-800 file:text-zinc-200 hover:file:bg-zinc-700"}),
        }
