from django.core.management.base import BaseCommand

from apps.inventory.seeds.imovel_category_seed import ImovelCategorySeed


class Command(BaseCommand):
    help = "Popula as categorias padrão de imóveis"

    def handle(self, *args, **options):
        self.stdout.write("🏠 Populando categorias de imóveis...")

        result = ImovelCategorySeed().run()

        self.stdout.write(self.style.SUCCESS(result))
