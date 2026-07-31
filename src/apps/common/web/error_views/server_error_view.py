from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views import View


class ServerErrorView(View):
    def dispatch(self, request, *args, **kwargs):
        # Django's handler500 is called without an HTTP-verb match and can fire
        # mid-failure (e.g. database down) — rendering without a request skips
        # context processors like organization_context, which query the
        # database and could otherwise turn this page into another 500.
        html = render_to_string("common/errors/500.html")
        return HttpResponse(html, status=500)
