from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def ts(source_path: str) -> str:
    """
    Resolve o caminho de um arquivo TypeScript fonte para o JS compilado em dist/.

    Uso:
        {% load assets %}
        <script src="{% ts 'common/js/cpf-register-validation.ts' %}"></script>

    Produz:
        <script src="/static/common/js/dist/cpf-register-validation.js"></script>
    """
    directory, _, filename = source_path.rpartition("/")
    js_filename = filename.removesuffix(".ts") + ".js"
    compiled_path = f"{directory}/dist/{js_filename}"
    return static(compiled_path)
