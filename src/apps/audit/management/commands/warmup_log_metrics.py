from django.core.management.base import BaseCommand

from apps.audit.file_metrics import FileMetricsStore
from apps.audit.services import LogReaderService


class Command(BaseCommand):
    help = "Reconstrói o snapshot de métricas a partir dos arquivos de log."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Janela de dias a considerar para o warm-up (padrão: 7).",
        )

    def handle(self, *args, **options):
        self.stdout.write("Reconstruindo snapshot de métricas dos arquivos de log...")
        scanned_layers = FileMetricsStore.rebuild_all(LogReaderService.LAYERS_MAP)
        self.stdout.write(self.style.SUCCESS(f"Warm-up concluído para {scanned_layers} camadas."))