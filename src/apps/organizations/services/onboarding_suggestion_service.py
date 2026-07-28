from django.utils.text import slugify

from apps.inventory.models import Category, Sector
from apps.organizations.onboarding_suggestions import INDUSTRY_SUGGESTIONS


class OnboardingSuggestionService:
    """Sugere categorias e setores de exemplo com base no setor de atuação da
    organização, pra acelerar o primeiro cadastro — Category e Sector são
    compartilhados entre organizações (sem FK própria), então só criamos os
    que ainda não existem, nunca duplicamos."""

    @staticmethod
    def get_suggestions(industry: str) -> dict:
        suggestions = INDUSTRY_SUGGESTIONS.get(industry, INDUSTRY_SUGGESTIONS["other"])

        existing_categories = set(Category.objects.values_list("name", flat=True))
        existing_sectors = set(Sector.objects.values_list("name", flat=True))

        return {
            "categories": [
                {"name": name, "exists": name in existing_categories}
                for name in suggestions["categories"]
            ],
            "sectors": [
                {"name": name, "exists": name in existing_sectors}
                for name in suggestions["sectors"]
            ],
        }

    @staticmethod
    def apply(category_names: list[str], sector_names: list[str], user) -> None:
        for name in category_names:
            Category.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "created_by": user, "updated_by": user},
            )
        for name in sector_names:
            Sector.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "created_by": user, "updated_by": user},
            )
