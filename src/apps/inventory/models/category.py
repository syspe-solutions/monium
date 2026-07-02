from django.db import models

from apps.common.models import BaseModelAbstract


class Category(BaseModelAbstract):
    name = models.CharField(max_length=150, verbose_name="Nome")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Slug")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
        verbose_name="Categoria pai",
    )
    description = models.TextField(blank=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
