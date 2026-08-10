from django.views.generic import TemplateView


class NotFoundView(TemplateView):
    template_name = "common/errors/404.html"

    def dispatch(self, request, *args, **kwargs):
        # Ver PermissionDeniedView.dispatch — handler404 também pode ser chamado
        # pra qualquer verbo HTTP.
        return self.render_to_response(self.get_context_data(**kwargs), status=404)
