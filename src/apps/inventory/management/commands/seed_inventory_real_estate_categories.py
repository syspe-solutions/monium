from django.core.management.base import BaseCommand

from apps.inventory.seeds.real_estate_category_seed import RealEstateCategorySeed


class Command(BaseCommand):
    help = "Popula as categorias padrão de imóveis"

    def handle(self, *args, **options):
        self.stdout.write("🏠 Populando categorias de imóveis...")

        result = RealEstateCategorySeed().run()

        self.stdout.write(self.style.SUCCESS(result))
