from django.core.management.base import BaseCommand

from apps.inventory.seeds.category_seed import CategorySeed


class Command(BaseCommand):
    help = "Popula as categorias padrão do inventário"

    def handle(self, *args, **options):
        self.stdout.write("📦 Populando categorias do inventário...")

        result = CategorySeed().run()

        self.stdout.write(self.style.SUCCESS(result))
