class BaseSeed:
    def is_populated(self, model, expected_count: int) -> bool:
        return model.objects.count() >= expected_count

    def populate_if_needed(self, model, data: list[dict], unique_field: str) -> str:
        created = 0

        for item in data:
            lookup = {unique_field: item[unique_field]}
            if not model.objects.filter(**lookup).exists():
                model.objects.create(**item)
                created += 1

        if created:
            return f"✔ {created} registros criados em {model._meta.verbose_name_plural}"
        return f"ℹ {model._meta.verbose_name_plural} já estavam populados"
