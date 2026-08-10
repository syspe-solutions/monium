from django.core.management.base import BaseCommand

from apps.inventory.tasks import check_expiring_warranties


class Command(BaseCommand):
    help = "Dispara o e-mail de aviso para garantias vencendo dentro da janela de alerta."

    def handle(self, *args, **options):
        notified = check_expiring_warranties()
        self.stdout.write(self.style.SUCCESS(f"{notified} aviso(s) de garantia enviado(s)."))
