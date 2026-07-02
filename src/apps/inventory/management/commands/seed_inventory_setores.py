from django.core.management.base import BaseCommand

from apps.inventory.seeds.sector_seed import SectorSeed


class Command(BaseCommand):
    help = "Popula os setores padrão do inventário"

    def handle(self, *args, **options):
        self.stdout.write("🏢 Populando setores do inventário...")

        result = SectorSeed().run()

        self.stdout.write(self.style.SUCCESS(result))
