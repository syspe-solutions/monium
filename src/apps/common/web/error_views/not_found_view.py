from django.views.generic import TemplateView


class NotFoundView(TemplateView):
    template_name = "common/errors/404.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs), status=404)
