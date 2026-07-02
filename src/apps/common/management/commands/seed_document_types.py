from django.core.management.base import BaseCommand

from apps.common.seeds.document_type_seed import DocumentTypeSeed


class Command(BaseCommand):
    help = "Popula os tipos de documentos padrão do sistema"

    def handle(self, *args, **options):
        self.stdout.write("📄 Populando tipos de documentos...")

        seed = DocumentTypeSeed()
        result = seed.run()

        self.stdout.write(self.style.SUCCESS(result))
