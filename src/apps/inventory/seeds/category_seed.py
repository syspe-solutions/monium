from apps.common.seeds.base_seed import BaseSeed
from apps.inventory.models import Category


class CategorySeed(BaseSeed):
    # useful_life_months segue a prática contábil comum no Brasil (bens de TI/
    # veículos depreciam mais rápido que móveis/máquinas); None = categoria não
    # depreciável (acervo, obras de arte, consumíveis) — o próprio model permite
    # deixar em branco pra isso.
    DATA = [
        # Mobiliário
        {"name": "Mobiliário de Escritório",              "slug": "mobiliario-de-escritorio",              "useful_life_months": 120},
        {"name": "Mobiliário de Apoio",                   "slug": "mobiliario-de-apoio",                   "useful_life_months": 120},
        {"name": "Estofados e Sofás",                     "slug": "estofados-e-sofas",                     "useful_life_months": 120},
        {"name": "Armários e Arquivos",                   "slug": "armarios-e-arquivos",                   "useful_life_months": 120},

        # Tecnologia da informação
        {"name": "Equipamentos de Informática",           "slug": "equipamentos-de-informatica",           "useful_life_months": 60},
        {"name": "Notebooks e Laptops",                   "slug": "notebooks-e-laptops",                   "useful_life_months": 60},
        {"name": "Servidores e Armazenamento",             "slug": "servidores-e-armazenamento",            "useful_life_months": 60},
        {"name": "Periféricos de Informática",             "slug": "perifericos-de-informatica",            "useful_life_months": 60},
        {"name": "Impressoras e Multifuncionais",         "slug": "impressoras-e-multifuncionais",         "useful_life_months": 60},
        {"name": "Redes e Telecomunicações",               "slug": "redes-e-telecomunicacoes",               "useful_life_months": 60},
        {"name": "Equipamentos de Telefonia Móvel",       "slug": "equipamentos-de-telefonia-movel",       "useful_life_months": 60},
        {"name": "Tablets e Dispositivos Móveis",         "slug": "tablets-e-dispositivos-moveis",         "useful_life_months": 60},

        # Audiovisual e comunicação
        {"name": "Equipamentos Audiovisuais",             "slug": "equipamentos-audiovisuais",             "useful_life_months": 60},
        {"name": "Equipamentos de Som e Iluminação",      "slug": "equipamentos-de-som-e-iluminacao",      "useful_life_months": 60},
        {"name": "Material Gráfico e Comunicação",        "slug": "material-grafico-e-comunicacao",        "useful_life_months": 60},
        {"name": "Sinalização e Placas",                  "slug": "sinalizacao-e-placas",                  "useful_life_months": 120},
        {"name": "Sistemas de Monitoramento (CFTV)",      "slug": "sistemas-de-monitoramento-cftv",        "useful_life_months": 60},

        # Eletrodomésticos e copa
        {"name": "Eletrodomésticos e Copa",               "slug": "eletrodomesticos-e-copa",                "useful_life_months": 120},
        {"name": "Equipamentos de Refrigeração",          "slug": "equipamentos-de-refrigeracao",          "useful_life_months": 120},
        {"name": "Equipamentos de Cozinha Industrial",    "slug": "equipamentos-de-cozinha-industrial",    "useful_life_months": 120},
        {"name": "Utensílios de Copa e Cozinha",          "slug": "utensilios-de-copa-e-cozinha",          "useful_life_months": 60},

        # Veículos
        {"name": "Veículos Leves",                        "slug": "veiculos-leves",                        "useful_life_months": 60},
        {"name": "Veículos Pesados e Utilitários",        "slug": "veiculos-pesados-e-utilitarios",        "useful_life_months": 60},
        {"name": "Motocicletas",                          "slug": "motocicletas",                          "useful_life_months": 60},
        {"name": "Embarcações",                           "slug": "embarcacoes",                           "useful_life_months": 60},

        # Máquinas, ferramentas e industrial
        {"name": "Máquinas e Equipamentos Industriais",   "slug": "maquinas-e-equipamentos-industriais",   "useful_life_months": 120},
        {"name": "Ferramentas e Manutenção",              "slug": "ferramentas-e-manutencao",              "useful_life_months": 120},
        {"name": "Equipamentos de Construção Civil",      "slug": "equipamentos-de-construcao-civil",      "useful_life_months": 120},
        {"name": "Equipamentos Agrícolas",                "slug": "equipamentos-agricolas",                "useful_life_months": 96},
        {"name": "Equipamentos de Transporte Interno",    "slug": "equipamentos-de-transporte-interno",    "useful_life_months": 120},
        {"name": "Geradores e Equipamentos de Energia",   "slug": "geradores-e-equipamentos-de-energia",   "useful_life_months": 120},
        {"name": "Equipamentos de Automação e Controle",  "slug": "equipamentos-de-automacao-e-controle",  "useful_life_months": 120},
        {"name": "Instrumentos de Medição e Calibração",  "slug": "instrumentos-de-medicao-e-calibracao",  "useful_life_months": 120},

        # Segurança
        {"name": "Equipamentos de Segurança",             "slug": "equipamentos-de-seguranca",             "useful_life_months": 120},
        {"name": "Equipamentos de Combate a Incêndio",    "slug": "equipamentos-de-combate-a-incendio",    "useful_life_months": 120},
        {"name": "Equipamentos de Proteção Individual",   "slug": "equipamentos-de-protecao-individual",   "useful_life_months": None},

        # Saúde e laboratório
        {"name": "Equipamentos Médicos e Hospitalares",   "slug": "equipamentos-medicos-e-hospitalares",   "useful_life_months": 120},
        {"name": "Equipamentos Laboratoriais",            "slug": "equipamentos-laboratoriais",            "useful_life_months": 120},
        {"name": "Equipamentos Odontológicos",            "slug": "equipamentos-odontologicos",            "useful_life_months": 120},

        # Esporte, lazer e cultura
        {"name": "Instrumentos Musicais",                 "slug": "instrumentos-musicais",                 "useful_life_months": 120},
        {"name": "Equipamentos Esportivos",               "slug": "equipamentos-esportivos",               "useful_life_months": 60},
        {"name": "Equipamentos de Academia",              "slug": "equipamentos-de-academia",              "useful_life_months": 120},
        {"name": "Acervo Bibliográfico",                  "slug": "acervo-bibliografico",                  "useful_life_months": None},
        {"name": "Obras de Arte e Decoração",             "slug": "obras-de-arte-e-decoracao",              "useful_life_months": None},

        # Outros
        {"name": "Vestuário e Uniformes",                 "slug": "vestuario-e-uniformes",                 "useful_life_months": 24},
        {"name": "Materiais de Limpeza e Higiene",        "slug": "materiais-de-limpeza-e-higiene",         "useful_life_months": None},
        {"name": "Equipamentos de Jardinagem",            "slug": "equipamentos-de-jardinagem",            "useful_life_months": 120},
        {"name": "Contêineres e Estruturas Modulares",    "slug": "conteineres-e-estruturas-modulares",    "useful_life_months": 120},
        {"name": "Bens de Uso Comum",                     "slug": "bens-de-uso-comum",                      "useful_life_months": None},
    ]

    def run(self) -> str:
        return self.populate_if_needed(
            model=Category,
            data=self.DATA,
            unique_field="slug",
        )
