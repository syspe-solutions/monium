from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.forms.category_useful_life_form import CategoryUsefulLifeForm
from apps.inventory.models import Category
from apps.organizations.mixins import InventoryWriteRequiredMixin


class CategoryUsefulLifeUpdateView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    """Categorias não pertencem a uma organização (taxonomia compartilhada da
    instância inteira, cadastrada via seed) — por isso não há get_object_or_404
    filtrando por organization aqui, diferente das views de item/imóvel."""

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        form = CategoryUsefulLifeForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            messages.success(request, _('Useful life for "%(name)s" updated.') % {"name": category.name})
        else:
            messages.error(request, _("Could not update useful life: %(errors)s") % {
                "errors": " ".join(form.errors.get("useful_life_months", []))
            })

        return redirect("inventory:dashboard")
