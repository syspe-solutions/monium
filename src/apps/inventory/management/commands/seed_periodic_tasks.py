from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Registra as tarefas periódicas do django_celery_beat (idempotente)"

    def handle(self, *args, **options):
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="6", day_of_week="*", day_of_month="*", month_of_year="*",
        )
        PeriodicTask.objects.update_or_create(
            name="inventory.check_overdue_loans",
            defaults={
                "crontab": schedule,
                "task": "apps.inventory.tasks.check_overdue_loans",
                "enabled": True,
            },
        )
        self.stdout.write(self.style.SUCCESS("Tarefa periódica 'inventory.check_overdue_loans' registrada (diária, 06:00)."))
