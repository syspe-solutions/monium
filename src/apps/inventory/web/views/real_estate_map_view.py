from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from apps.inventory.models import RealEstateAsset


class RealEstateMapView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/real_estate_map.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization

        real_estate_assets = RealEstateAsset.objects.filter(organization=organization).select_related("category")

        ctx["total_count"] = real_estate_assets.count()
        ctx["properties"] = self._serialize_properties(real_estate_assets)
        ctx["missing_coordinates_count"] = ctx["total_count"] - len(ctx["properties"])
        return ctx

    def _serialize_properties(self, real_estate_assets):
        return [
            {
                "name": real_estate.name,
                "code": real_estate.code,
                "address": real_estate.address,
                "category": real_estate.category.name,
                "latitude": float(real_estate.latitude),
                "longitude": float(real_estate.longitude),
                "url": reverse("inventory:real_estate_detail", args=[real_estate.id]),
            }
            for real_estate in real_estate_assets
            if real_estate.latitude is not None and real_estate.longitude is not None
        ]
