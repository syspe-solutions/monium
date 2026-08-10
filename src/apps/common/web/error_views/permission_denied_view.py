from django.views.generic import TemplateView


class PermissionDeniedView(TemplateView):
    template_name = "common/errors/403.html"

    def dispatch(self, request, *args, **kwargs):
        # handler403 pode ser chamado pra qualquer verbo HTTP (um PermissionDenied
        # levantado num POST/PUT/DELETE é tão válido quanto num GET) — o dispatch
        # padrão de View só despacha pro método que dá nome ao verbo, então um
        # handler403 com apenas get() vira 405 em vez de 403 nesses casos.
        return self.render_to_response(self.get_context_data(**kwargs), status=403)
