from django.views.generic import TemplateView


class PermissionDeniedView(TemplateView):
    template_name = "common/errors/403.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs), status=403)
