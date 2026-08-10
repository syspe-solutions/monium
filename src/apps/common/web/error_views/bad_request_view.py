from django.views.generic import TemplateView


class BadRequestView(TemplateView):
    template_name = "common/errors/400.html"

    def dispatch(self, request, *args, **kwargs):
        # Ver PermissionDeniedView.dispatch — handler400 também pode ser chamado
        # pra qualquer verbo HTTP.
        return self.render_to_response(self.get_context_data(**kwargs), status=400)
