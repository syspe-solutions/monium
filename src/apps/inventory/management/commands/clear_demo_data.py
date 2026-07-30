from django.core.management.base import BaseCommand
from django.db import transaction

from apps.inventory.management.commands.populate_demo_data import (
    DEMO_ORG_SLUG,
)
from apps.inventory.models import (
    Brand,
    Category,
    ImovelCategory,
    Loan,
    Location,
    Maintenance,
    Movement,
    MovelSpec,
    Sector,
)
from apps.organizations.models import Organization


class Command(BaseCommand):
    help = (
        "Remove a organização de demonstração ('Organização Demo') criada por "
        "'populate_demo_data', junto com seus itens, imóveis, fotos e as categorias/"
        "setores/marcas exclusivas de demonstração. Não afeta nenhuma outra organização."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        organization = Organization.objects.filter(slug=DEMO_ORG_SLUG).first()

        if organization is None:
            self.stdout.write(self.style.WARNING(
                "Nenhuma organização demo encontrada — nada a remover."
            ))
            return

        # Remove os arquivos de imagem do disco/storage antes do cascade apagar as
        # linhas do banco — o Django não faz isso sozinho ao deletar via CASCADE.
        specs_with_image = MovelSpec.objects.filter(
            movel__organization=organization, image__isnull=False,
        ).exclude(image="")
        removed_images = 0
        for spec in specs_with_image:
            spec.image.delete(save=False)
            removed_images += 1

        # Empréstimos, manutenções e movimentações protegem o item contra exclusão
        # (on_delete=PROTECT) — precisam sumir antes do cascade da organização, senão
        # o delete inteiro falha com ProtectedError.
        removed_loans, _ = Loan.objects.filter(item__organization=organization).delete()
        removed_maintenances, _ = Maintenance.objects.filter(item__organization=organization).delete()
        Movement.objects.filter(item__organization=organization).delete()

        organization_name = organization.name
        organization.delete()
        self.stdout.write(self.style.SUCCESS(
            f"Organização '{organization_name}' removida (itens, imóveis, membros, "
            f"{removed_images} foto(s), {removed_loans} empréstimo(s) e "
            f"{removed_maintenances} manutenção(ões) de exemplo apagados em cascata)."
        ))

        # Location protege o setor contra exclusão (on_delete=PROTECT) — some antes.
        removed_locations, _ = Location.objects.filter(sector__slug__startswith="demo-").delete()
        removed_categories, _ = Category.objects.filter(slug__startswith="demo-").delete()
        removed_sectors, _ = Sector.objects.filter(slug__startswith="demo-").delete()
        removed_brands, _ = Brand.objects.filter(slug__startswith="demo-").delete()
        removed_imovel_categories, _ = ImovelCategory.objects.filter(slug__startswith="demo-").delete()
        self.stdout.write(f"Removida(s) {removed_locations} localização(ões) de demonstração.")

        self.stdout.write(self.style.SUCCESS(
            "Dados de referência de demonstração removidos: "
            f"{removed_categories} categoria(s), {removed_sectors} setor(es), "
            f"{removed_brands} marca(s), {removed_imovel_categories} categoria(s) de imóvel."
        ))
