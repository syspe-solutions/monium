from django.views.generic import TemplateView


class BadRequestView(TemplateView):
    template_name = "common/errors/400.html"

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs), status=400)
