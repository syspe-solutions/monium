from django.core.management.base import BaseCommand

from apps.inventory.tasks import check_overdue_loans


class Command(BaseCommand):
    help = "Marca empréstimos vencidos como atrasados e dispara o e-mail de aviso."

    def handle(self, *args, **options):
        updated = check_overdue_loans()
        self.stdout.write(self.style.SUCCESS(f"{updated} empréstimo(s) marcado(s) como atrasado(s)."))
