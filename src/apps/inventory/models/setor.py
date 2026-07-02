from django.db import models

from apps.common.models import BaseModelAbstract


class Setor(BaseModelAbstract):
    name = models.CharField(max_length=150, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Slug")
    responsible = models.CharField(max_length=255, blank=True, verbose_name="Responsável")
    description = models.TextField(blank=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Setor"
        verbose_name_plural = "Setores"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Location(BaseModelAbstract):
    setor = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        related_name="locations",
        verbose_name="Setor",
    )
    name = models.CharField(max_length=150, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Localização"
        verbose_name_plural = "Localizações"
        ordering = ["setor", "name"]

    def __str__(self):
        return f"{self.name} — {self.setor.name}"
