from django.db import models

from apps.common.models import BaseModelAbstract


class Supplier(BaseModelAbstract):
    name = models.CharField(max_length=255, verbose_name="Nome")
    cnpj = models.CharField(max_length=18, blank=True, verbose_name="CNPJ")
    contact_name = models.CharField(max_length=255, blank=True, verbose_name="Contato")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, verbose_name="E-mail")

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["name"]

    def __str__(self):
        return self.name
