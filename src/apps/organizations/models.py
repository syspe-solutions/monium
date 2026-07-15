import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import BaseModelAbstract


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
    MEMBER = "member", "Membro"


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


class InvitationStatus(models.TextChoices):
    PENDING = "pending", "Pendente"
    ACCEPTED = "accepted", "Aceito"
    REVOKED = "revoked", "Revogado"


INVITATION_EXPIRY_DAYS = 7


def default_invitation_expiry():
    return timezone.now() + timedelta(days=INVITATION_EXPIRY_DAYS)


class Invitation(BaseModelAbstract):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name="Organização",
    )
    email = models.EmailField(verbose_name="E-mail")
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER,
        verbose_name="Papel",
    )
    token = models.CharField(max_length=64, unique=True, editable=False)
    status = models.CharField(
        max_length=20,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING,
        verbose_name="Status",
    )
    expires_at = models.DateTimeField(default=default_invitation_expiry, verbose_name="Expira em")
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_invitations",
    )

    class Meta:
        verbose_name = "Convite"
        verbose_name_plural = "Convites"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "email"],
                condition=models.Q(status=InvitationStatus.PENDING),
                name="unique_pending_invitation_per_org_email",
            ),
        ]

    def __str__(self):
        return f"{self.email} -> {self.organization} ({self.status})"

    @property
    def is_expired(self) -> bool:
        return self.status == InvitationStatus.PENDING and timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)
