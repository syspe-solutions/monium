from django.core.management.base import BaseCommand

from apps.common.seeds.location_seed import LocationSeed


class Command(BaseCommand):
    help = "Popula as regiões de desenvolvimento e seus municipios."

    def handle(self, *args, **options):
        self.stdout.write("📍 Populando regiões e municipios...")

        seed = LocationSeed()
        result = seed.run()

        self.stdout.write(self.style.SUCCESS(result))
