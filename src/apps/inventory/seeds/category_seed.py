from apps.common.seeds.base_seed import BaseSeed
from apps.inventory.models import Category


class CategorySeed(BaseSeed):
    DATA = [
        {"name": "Eletrodomésticos e Copa",          "slug": "eletrodomesticos-e-copa"},
        {"name": "Material Gráfico e Comunicação",   "slug": "material-grafico-e-comunicacao"},
        {"name": "Mobiliário de Escritório",         "slug": "mobiliario-de-escritorio"},
        {"name": "Mobiliário de Apoio",              "slug": "mobiliario-de-apoio"},
        {"name": "Equipamentos de Informática",      "slug": "equipamentos-de-informatica"},
        {"name": "Equipamentos Audiovisuais",        "slug": "equipamentos-audiovisuais"},
        {"name": "Equipamentos de Segurança",        "slug": "equipamentos-de-seguranca"},
        {"name": "Ferramentas e Manutenção",         "slug": "ferramentas-e-manutencao"},
        {"name": "Telecomunicações",                 "slug": "telecomunicacoes"},
    ]

    def run(self) -> str:
        return self.populate_if_needed(
            model=Category,
            data=self.DATA,
            unique_field="slug",
        )
