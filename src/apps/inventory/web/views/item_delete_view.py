from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.models import MovableAsset
from apps.organizations.mixins import InventoryWriteRequiredMixin


class MovableAssetDeleteView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    template_name = "inventory/item_delete_confirm.html"

    def _get_item(self, request, pk):
        return get_object_or_404(MovableAsset, pk=pk, organization=request.organization)

    def _blocking_counts(self, item):
        return {
            "loans": item.loans.count(),
            "maintenances": item.maintenances.count(),
            "movements": item.movements.count(),
        }

    def get(self, request, pk):
        item = self._get_item(request, pk)
        return render(request, self.template_name, {
            "item": item,
            "blocking": self._blocking_counts(item),
        })

    def post(self, request, pk):
        item = self._get_item(request, pk)
        blocking = self._blocking_counts(item)

        if any(blocking.values()):
            messages.error(request, _(
                'Item "%(name)s" cannot be permanently deleted because it has loan, maintenance or '
                "movement history. Mark it as \"Written Off\" instead to keep it out of active use "
                "while preserving its history."
            ) % {"name": item.name})
            return redirect("inventory:item_detail", pk=item.id)

        confirmation = request.POST.get("confirmation_code", "").strip()
        if confirmation != item.code:
            messages.error(request, _("The typed code doesn't match. The item was not deleted."))
            return render(request, self.template_name, {
                "item": item,
                "blocking": blocking,
            })

        name = item.name
        spec = getattr(item, "spec", None)
        if spec and spec.image:
            spec.image.delete(save=False)

        item.delete()
        messages.success(request, _('Item "%(name)s" deleted.') % {"name": name})
        return redirect("inventory:item_list")
