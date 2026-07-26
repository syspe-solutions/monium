from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views import View

from apps.inventory.forms.movel_form import MovelForm, MovelSpecForm
from apps.inventory.models import Brand
from apps.organizations.mixins import InventoryWriteRequiredMixin

from .brand_views import find_similar_brands


class MovelCreateView(LoginRequiredMixin, InventoryWriteRequiredMixin, View):
    template_name = "inventory/item_form.html"
    success_url = reverse_lazy("inventory:dashboard")

    def _context(self, form, spec_form, selected_brand_id="", brand_error=""):
        return {
            "form": form,
            "spec_form": spec_form,
            "brands": Brand.objects.order_by("name"),
            "selected_brand_id": str(selected_brand_id),
            "brand_error": brand_error,
        }

    def get(self, request):
        return render(request, self.template_name,
                      self._context(MovelForm(), MovelSpecForm()))

    def post(self, request):
        form = MovelForm(request.POST)
        spec_form = MovelSpecForm(request.POST, request.FILES)
        brand_id = request.POST.get("brand_id", "").strip()
        new_brand_name = request.POST.get("new_brand_name", "").strip()

        if not form.is_valid() or not spec_form.is_valid():
            return render(request, self.template_name,
                          self._context(form, spec_form, brand_id))

        organization = request.organization

        # Resolve brand
        brand_instance = None
        brand_error = ""

        if brand_id and brand_id != "__new__":
            try:
                brand_instance = Brand.objects.get(id=brand_id)
            except Brand.DoesNotExist:
                brand_error = _("Selected brand not found.")
        elif new_brand_name:
            similar = find_similar_brands(new_brand_name)
            if similar:
                closest = similar[0][0].name
                brand_error = _(
                    'A very similar brand already exists: "%(name)s". Select it from the list or choose a '
                    "different name."
                ) % {"name": closest}
            else:
                brand_instance = Brand.objects.create(
                    name=new_brand_name,
                    created_by=request.user,
                    updated_by=request.user,
                )

        if brand_error:
            return render(request, self.template_name,
                          self._context(form, spec_form, "__new__", brand_error))

        # Save item
        item = form.save(commit=False)
        item.organization = organization
        item.created_by = request.user
        item.updated_by = request.user
        item.save()

        # Save spec if any data provided
        has_spec = any([
            brand_instance,
            spec_form.cleaned_data.get("model_name"),
            spec_form.cleaned_data.get("serial_number"),
            spec_form.cleaned_data.get("image"),
        ])
        if has_spec:
            spec = spec_form.save(commit=False)
            spec.movel = item
            spec.brand = brand_instance
            spec.created_by = request.user
            spec.updated_by = request.user
            spec.save()

        messages.success(request, _('Item "%(name)s" registered successfully.') % {"name": item.name})
        return redirect(self.success_url)
