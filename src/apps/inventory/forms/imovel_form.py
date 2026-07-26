from django import forms

from apps.inventory.models import Imovel

_INPUT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600"
_SELECT = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white focus:outline-none focus:ring-2 focus:ring-zinc-600"
_TEXTAREA = "w-full p-2 border border-zinc-700 rounded text-sm bg-zinc-900 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-zinc-600 resize-none"


class ImovelForm(forms.ModelForm):
    class Meta:
        model = Imovel
        fields = [
            "code", "name", "description",
            "category", "responsible", "ownership",
            "cartorio_situacao", "cep", "address", "zone", "latitude", "longitude",
            "total_area", "built_area",
            "condition", "notes",
        ]
        widgets = {
            "code":              forms.TextInput(attrs={"class": _INPUT, "placeholder": "Ex: IMV-0001", "autofocus": True}),
            "name":              forms.TextInput(attrs={"class": _INPUT, "placeholder": "Nome do imóvel"}),
            "description":       forms.Textarea(attrs={"class": _TEXTAREA, "rows": 3, "placeholder": "Descrição opcional"}),
            "category":          forms.Select(attrs={"class": _SELECT}),
            "responsible":       forms.TextInput(attrs={"class": _INPUT, "placeholder": "Nome do responsável"}),
            "ownership":         forms.Select(attrs={"class": _SELECT}),
            "cartorio_situacao": forms.Select(attrs={"class": _SELECT}),
            "cep":               forms.TextInput(attrs={"class": _INPUT, "placeholder": "00000-000"}),
            "address":           forms.TextInput(attrs={"class": _INPUT, "placeholder": "Rua, número, bairro, cidade/UF"}),
            "zone":              forms.Select(attrs={"class": _SELECT}),
            "latitude":          forms.TextInput(attrs={"class": _INPUT, "placeholder": "Ex: -23.550520"}),
            "longitude":         forms.TextInput(attrs={"class": _INPUT, "placeholder": "Ex: -46.633308"}),
            "total_area":        forms.TextInput(attrs={"class": _INPUT, "placeholder": "Área total em m²"}),
            "built_area":        forms.TextInput(attrs={"class": _INPUT, "placeholder": "Área construída em m²"}),
            "condition":         forms.Select(attrs={"class": _SELECT}),
            "notes":             forms.Textarea(attrs={"class": _TEXTAREA, "rows": 3, "placeholder": "Observações"}),
        }
