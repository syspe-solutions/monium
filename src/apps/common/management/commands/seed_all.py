from django.core.management.base import BaseCommand

from apps.account.seeds.directorate_seed import DirectorateSeed
from apps.account.seeds.extra_permissions_seed import ExtraPermissionsSeed
from apps.account.seeds.hierarchy_seed import HierarchySeed
from apps.account.seeds.role_level_seed import RoleLevelSeed
from apps.account.seeds.sector_seed import SectorSeed
from apps.business.seeds.bank_account_type_seed import BankAccountTypeSeed
from apps.business.seeds.constitution_type_seed import ConstitutionTypeSeed
from apps.business.seeds.credit_line_seed import CreditLineSeed
from apps.business.seeds.enterprise_industry_seed import EnterpriseIndustrySeed
from apps.business.seeds.enterprise_type_seed import EnterpriseTypeSeed
from apps.business.seeds.financial_institution_seed import FinancialInstitutionSeed
from apps.business.seeds.step_status_seed import StepStatusSeed
from apps.business.seeds.step_type_seed import StepTypeSeed
from apps.common.seeds.document_type_seed import DocumentTypeSeed
from apps.common.seeds.location_seed import LocationSeed
from apps.customer.seeds.educational_level_seed import EducationalLevelSeed
from apps.customer.seeds.gender_seed import GenderSeed
from apps.customer.seeds.marital_status_seed import MaritalStatusSeed
from apps.business.seeds.credit_step_seed import CreditStepSeed
from apps.business.seeds.lse_structure_seed import LSEStructureSeed

SEEDS = [
    ("📍 Regiões e municípios",         LocationSeed),
    ("📄 Tipos de documento",           DocumentTypeSeed),
    ("🏛️ Diretorias",                   DirectorateSeed),
    ("🏢 Setores",                      SectorSeed),
    ("📊 Hierarquias",                  HierarchySeed),
    ("🎖️ Níveis de cargo",              RoleLevelSeed),
    ("🔑 Permissões extras",            ExtraPermissionsSeed),
    ("⚧️ Gêneros",                      GenderSeed),
    ("💍 Estados civis",                MaritalStatusSeed),
    ("🎓 Níveis de escolaridade",       EducationalLevelSeed),
    ("🏪 Tipos de empreendimento",      EnterpriseTypeSeed),
    ("🏭 Ramos de atividade",           EnterpriseIndustrySeed),
    ("📜 Tipos de constituição",        ConstitutionTypeSeed),
    ("🏦 Tipos de conta bancária",      BankAccountTypeSeed),
    ("🏦 Instituições financeiras",     FinancialInstitutionSeed),
    ("💳 Linhas de crédito",            CreditLineSeed),
    ("📋 Estrutura LSE",                LSEStructureSeed),
    ("🔢 Tipos de etapa",               StepTypeSeed),
    ("🔵 Status de etapa",              StepStatusSeed),
    ("📑 Etapas de crédito",            CreditStepSeed),
]


class Command(BaseCommand):
    help = "Executa todos os seeds do projeto em ordem."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Executando todos os seeds ===\n"))

        success = 0
        errors = 0

        for label, SeedClass in SEEDS:
            self.stdout.write(f"{label}...")
            try:
                result = SeedClass().run()
                self.stdout.write(self.style.SUCCESS(f"  {result}"))
                success += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"  ✖ Erro: {exc}"))
                errors += 1

        self.stdout.write("")
        if errors:
            self.stdout.write(self.style.WARNING(
                f"Concluído com {success} seeds executados e {errors} erro(s)."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Concluído! {success} seeds executados com sucesso."
            ))
