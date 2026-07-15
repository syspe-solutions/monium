from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from apps.inventory.forms.imovel_filter_form import ImovelFilterForm
from apps.inventory.services.imovel_filters import filter_imoveis

PAGE_SIZE = 25


class ImovelListView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/imovel_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        organization = self.request.organization

        form = ImovelFilterForm(self.request.GET or None)
        filters = form.cleaned_data if form.is_valid() else {}
        imoveis = filter_imoveis(organization, filters)

        paginator = Paginator(imoveis, PAGE_SIZE)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        querystring = self.request.GET.copy()
        querystring.pop("page", None)

        ctx["form"] = form
        ctx["page_obj"] = page_obj
        ctx["imoveis"] = page_obj.object_list
        ctx["total_count"] = paginator.count
        ctx["filter_querystring"] = querystring.urlencode()
        return ctx
