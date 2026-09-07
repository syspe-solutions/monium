from apps.common.seeds.base_seed import BaseSeed
from apps.inventory.models import RealEstateCategory


class RealEstateCategorySeed(BaseSeed):
    DATA = [
        {"name": "Casa",                              "slug": "casa"},
        {"name": "Sobrado",                            "slug": "sobrado"},
        {"name": "Apartamento",                        "slug": "apartamento"},
        {"name": "Kitnet / Studio",                    "slug": "kitnet-studio"},
        {"name": "Cobertura",                          "slug": "cobertura"},
        {"name": "Terreno Urbano",                     "slug": "terreno-urbano"},
        {"name": "Terreno Rural",                      "slug": "terreno-rural"},
        {"name": "Sala Comercial",                     "slug": "sala-comercial"},
        {"name": "Loja / Ponto Comercial",             "slug": "loja-ponto-comercial"},
        {"name": "Galpão / Depósito",                  "slug": "galpao-deposito"},
        {"name": "Prédio / Edifício",                  "slug": "predio-edificio"},
        {"name": "Área Industrial",                    "slug": "area-industrial"},
        {"name": "Estacionamento / Garagem",           "slug": "estacionamento-garagem"},
        {"name": "Escritório Compartilhado / Coworking", "slug": "escritorio-compartilhado-coworking"},
        {"name": "Sítio / Chácara / Fazenda",          "slug": "sitio-chacara-fazenda"},
        {"name": "Área Rural Produtiva",               "slug": "area-rural-produtiva"},
        {"name": "Imóvel em Construção",               "slug": "imovel-em-construcao"},
        {"name": "Imóvel Institucional / Público",     "slug": "imovel-institucional-publico"},
    ]

    def run(self) -> str:
        return self.populate_if_needed(
            model=RealEstateCategory,
            data=self.DATA,
            unique_field="slug",
        )
