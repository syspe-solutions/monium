import uuid

from django.conf import settings
from django.db import models

from apps.common.models import BaseModelAbstract


def organization_logo_upload_path(instance, filename):
    ext = filename.split(".")[-1].lower()
    return f"organizations/{instance.id}/{uuid.uuid4().hex}.{ext}"


class OrganizationIndustry(models.TextChoices):
    TECHNOLOGY = "technology", "Tecnologia"
    EDUCATION = "education", "Educação"
    HEALTHCARE = "healthcare", "Saúde"
    RETAIL = "retail", "Varejo / Comércio"
    MANUFACTURING = "manufacturing", "Indústria"
    SERVICES = "services", "Serviços"
    CONSTRUCTION = "construction", "Construção civil"
    PUBLIC_SECTOR = "public_sector", "Órgão público"
    OTHER = "other", "Outro"


class OrganizationSize(models.TextChoices):
    MICRO = "1-10", "1 a 10 pessoas"
    SMALL = "11-50", "11 a 50 pessoas"
    MEDIUM = "51-200", "51 a 200 pessoas"
    LARGE = "200+", "Mais de 200 pessoas"


class OrganizationGoal(models.TextChoices):
    IT_EQUIPMENT = "it_equipment", "Equipamentos de TI"
    FIXED_ASSETS = "fixed_assets", "Patrimônio / ativos fixos"
    TOOLS = "tools", "Ferramentas"
    INTERNAL_LOANS = "internal_loans", "Empréstimos internos"
    MAINTENANCE = "maintenance", "Manutenção de equipamentos"
    OTHER = "other", "Outro"


class Organization(BaseModelAbstract):
    name = models.CharField(max_length=150, verbose_name="Nome")
    slug = models.SlugField(max_length=160, unique=True, verbose_name="Slug")
    logo = models.ImageField(
        upload_to=organization_logo_upload_path,
        null=True,
        blank=True,
        verbose_name="Logo",
    )
    industry = models.CharField(
        max_length=30,
        choices=OrganizationIndustry.choices,
        verbose_name="Setor de atuação",
    )
    size = models.CharField(
        max_length=10,
        choices=OrganizationSize.choices,
        verbose_name="Porte da equipe",
    )
    primary_goal = models.CharField(
        max_length=30,
        choices=OrganizationGoal.choices,
        verbose_name="Principal uso pretendido",
    )

    class Meta:
        verbose_name = "Organização"
        verbose_name_plural = "Organizações"

    def __str__(self):
        return self.name


class MembershipRole(models.TextChoices):
    OWNER = "owner", "Proprietário"
    ADMIN = "admin", "Administrador"
    MANAGER = "manager", "Gerente"
    OPERATOR = "operator", "Operador"
    VIEWER = "viewer", "Visualizador"


# Papéis que podem gerenciar membros (criar, remover, trocar papel de outros).
_MEMBER_MANAGEMENT_ROLES = {MembershipRole.OWNER, MembershipRole.ADMIN}

# Papéis que podem cadastrar/importar itens e imóveis.
_INVENTORY_WRITE_ROLES = {
    MembershipRole.OWNER,
    MembershipRole.ADMIN,
    MembershipRole.MANAGER,
    MembershipRole.OPERATOR,
}

# Papéis atribuíveis por quem gerencia membros — OWNER não é atribuível aqui,
# transferência de propriedade é um fluxo separado (fora do escopo atual).
ASSIGNABLE_MEMBERSHIP_ROLES = [
    MembershipRole.ADMIN,
    MembershipRole.MANAGER,
    MembershipRole.OPERATOR,
    MembershipRole.VIEWER,
]


class Membership(BaseModelAbstract):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="Organização",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="Usuário",
    )
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.OWNER,
        verbose_name="Papel",
    )

    class Meta:
        verbose_name = "Membro da organização"
        verbose_name_plural = "Membros da organização"
        constraints = [
            models.UniqueConstraint(fields=["user", "organization"], name="unique_membership_user_org"),
        ]

    def __str__(self):
        return f"{self.user} @ {self.organization}"

    def can_manage_members(self) -> bool:
        return self.role in _MEMBER_MANAGEMENT_ROLES

    def can_write_inventory(self) -> bool:
        return self.role in _INVENTORY_WRITE_ROLES
