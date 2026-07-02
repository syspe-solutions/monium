from apps.common.seeds.base_seed import BaseSeed
from apps.inventory.models import Sector


class SectorSeed(BaseSeed):
    DATA = [
        {"name": "Superintendência Júridica",                   "slug": "sujur"},
        {"name": "Assessoria de Comunicação",                   "slug": "ascom"},
        {"name": "Assessoria Jurídica",                         "slug": "asjur"},
        {"name": "Auditoria Interna",                           "slug": "audin"},
        {"name": "Comissão Permanente de Licitação",            "slug": "cpl"},
        {"name": "Gerência de Compliance e Controle Interno",   "slug": "gecoi"},
        {"name": "Ouvidoria",                                   "slug": "ouvidoria"},
        {"name": "Gerência Administrativa",                     "slug": "gerad"},
        {"name": "Gerência de Recursos Humanos",                "slug": "rh"},
        {"name": "Gerência de Planejamento e Análise de Dados", "slug": "gplad"},
        {"name": "Superintendência de Tecnologia da Informação","slug": "sutic"},
        {"name": "Superintendência de Crédito",                 "slug": "sucre"},
        {"name": "Gerência de Contabilidade",                   "slug": "gecon"},
        {"name": "Gerência de Análise de Cobrança",             "slug": "geanc"},
        {"name": "Superintendência Financeira",                 "slug": "sufin"},
        {"name": "Superintendência de Operações",               "slug": "suope"},
        {"name": "Superintendência de Pequenos Negócios",       "slug": "supen"},
    ]

    def run(self) -> str:
        return self.populate_if_needed(
            model=Sector,
            data=self.DATA,
            unique_field="slug",
        )
