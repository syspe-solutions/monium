from apps.common.seeds.base_seed import BaseSeed
from apps.inventory.models import RealEstateCategory


class RealEstateCategorySeed(BaseSeed):
    DATA = [
        {"name": "Casa",                       "slug": "casa"},
        {"name": "Apartamento",                "slug": "apartamento"},
        {"name": "Terreno",                    "slug": "terreno"},
        {"name": "Sala Comercial",             "slug": "sala-comercial"},
        {"name": "Galpão / Depósito",          "slug": "galpao-deposito"},
        {"name": "Prédio / Edifício",          "slug": "predio-edificio"},
        {"name": "Sítio / Chácara / Fazenda",  "slug": "sitio-chacara-fazenda"},
    ]

    def run(self) -> str:
        return self.populate_if_needed(
            model=RealEstateCategory,
            data=self.DATA,
            unique_field="slug",
        )
