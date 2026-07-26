from django.core.management import call_command
from django.db import migrations

CACHE_TABLE_NAME = "django_cache"


def create_cache_table(apps, schema_editor):
    call_command("createcachetable", CACHE_TABLE_NAME)


def drop_cache_table(apps, schema_editor):
    schema_editor.execute(f"DROP TABLE IF EXISTS {CACHE_TABLE_NAME}")


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_cache_table, drop_cache_table),
    ]
