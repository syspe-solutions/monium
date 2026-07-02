import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


# modelo base abstrato para outros modelos
class BaseModelAbstract(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        unique=True
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(class)s_created',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='%(class)s_updated',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False
    )

    class Meta:
        abstract = True


# endereço
class Address(BaseModelAbstract):
    street = models.CharField(
        max_length=255, 
        verbose_name="Logradouro"
    )
    city = models.CharField(
        max_length=128,
        verbose_name="Cidade"
    )
    district = models.CharField(
        max_length=128, 
        verbose_name="Bairro"
    )
    zip_code = models.CharField(
        max_length=20, 
        verbose_name="CEP"
    )
    number = models.CharField(
        max_length=20, 
        verbose_name="Número"
    )
    complement = models.CharField(
        null=True,
        blank=True, 
        max_length=255, 
        verbose_name="Complemento"
    )
    state = models.CharField(
        default="PE",
        max_length=2,
        verbose_name="Estado"
    )

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    def __str__(self):
        return f"{self.street}, {self.number} - {self.city}"





class DevelopmentRegion(BaseModelAbstract):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nome da Região"
    )

    acronym = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Sigla da Região"
    )

    class Meta:
        verbose_name = "Região de Desenvolvimento"
        verbose_name_plural = "Regiões de Desenvolvimento"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Municipality(BaseModelAbstract):
    region = models.ForeignKey(
        DevelopmentRegion,
        on_delete=models.PROTECT,
        related_name="municipalities",
        verbose_name="Região de Desenvolvimento"
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Nome do Município"
    )

    ibge_code = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código IBGE"
    )

    class Meta:
        verbose_name = "Município"
        verbose_name_plural = "Municípios"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["region", "name"],
                name="unique_municipality_per_region"
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.region.name}"



class StoredFile(BaseModelAbstract): 
    relative_path = models.CharField(max_length=255, unique=False)
    
    