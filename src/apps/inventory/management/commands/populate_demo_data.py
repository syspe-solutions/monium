import random
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw

from apps.inventory.models import (
    Acquisition,
    AssetOwnership,
    Brand,
    CartorioSituacao,
    Category,
    Imovel,
    ImovelCategory,
    ItemCondition,
    Loan,
    LoanStatus,
    Location,
    Maintenance,
    MaintenanceStatus,
    Movel,
    MovelSpec,
    MovelStatus,
    Sector,
    ZonaTipo,
)
from apps.organizations.models import (
    Membership,
    MembershipRole,
    Organization,
    OrganizationGoal,
    OrganizationIndustry,
    OrganizationSize,
)

DEMO_ORG_SLUG = "organizacao-demo"
RNG_SEED = 42

# "weight" define a frequência relativa da categoria/setor no inventário gerado —
# sem isso, a distribuição por índice ficava artificialmente equilibrada (mesma
# quantidade de itens em cada categoria/setor), o que não parece um dado real.
DEMO_CATEGORIES = [
    {"name": "Informática (Demo)", "slug": "demo-informatica", "color": (52, 101, 164), "weight": 30},
    {"name": "Mobiliário (Demo)", "slug": "demo-mobiliario", "color": (117, 80, 123), "weight": 22},
    {"name": "Eletrodomésticos (Demo)", "slug": "demo-eletrodomesticos", "color": (78, 154, 6), "weight": 10},
    {"name": "Ferramentas (Demo)", "slug": "demo-ferramentas", "color": (196, 160, 0), "weight": 8},
    {"name": "Audiovisual (Demo)", "slug": "demo-audiovisual", "color": (32, 74, 135), "weight": 7},
    {"name": "Segurança (Demo)", "slug": "demo-seguranca", "color": (161, 47, 47), "weight": 6},
    {"name": "Veículos (Demo)", "slug": "demo-veiculos", "color": (85, 87, 83), "weight": 4},
    {"name": "Copa e Cozinha (Demo)", "slug": "demo-copa-cozinha", "color": (206, 92, 0), "weight": 8},
    {"name": "Jardim e Externos (Demo)", "slug": "demo-externos", "color": (46, 125, 50), "weight": 5},
]

DEFAULT_ITEM_COUNT = 220

DEMO_SECTORS = [
    {"name": "TI (Demo)", "slug": "demo-ti", "weight": 20},
    {"name": "Administrativo (Demo)", "slug": "demo-administrativo", "weight": 16},
    {"name": "Financeiro (Demo)", "slug": "demo-financeiro", "weight": 9},
    {"name": "Recursos Humanos (Demo)", "slug": "demo-rh", "weight": 7},
    {"name": "Manutenção (Demo)", "slug": "demo-manutencao", "weight": 10},
    {"name": "Almoxarifado (Demo)", "slug": "demo-almoxarifado", "weight": 18},
    {"name": "Comercial (Demo)", "slug": "demo-comercial", "weight": 8},
    {"name": "Marketing (Demo)", "slug": "demo-marketing", "weight": 4},
    {"name": "Diretoria (Demo)", "slug": "demo-diretoria", "weight": 3},
    {"name": "Produção (Demo)", "slug": "demo-producao", "weight": 5},
]

# Marcas plausíveis por categoria — evita combinações estranhas (ex: "Furadeira
# Herman Miller") e aumenta a variação percebida sem precisar de listas gigantes.
BRANDS_BY_CATEGORY = {
    "demo-informatica": ["Dell", "HP", "Lenovo", "Positivo", "Acer", "Asus", "Apple", "Samsung", "Logitech"],
    "demo-mobiliario": ["Herman Miller", "Flexform", "Carraro", "Pormade", "Tok Stok"],
    "demo-eletrodomesticos": ["Samsung", "LG", "Electrolux", "Brastemp", "Consul", "Philips"],
    "demo-ferramentas": ["Bosch", "Makita", "Vonder", "DeWalt", "Tramontina"],
    "demo-audiovisual": ["Sony", "JBL", "Samsung", "LG", "Epson", "Canon"],
    "demo-seguranca": ["Intelbras", "Hikvision", "JFL"],
    "demo-veiculos": ["Fiat", "Volkswagen", "Chevrolet", "Honda", "Toyota"],
    "demo-copa-cozinha": ["Electrolux", "Consul", "Britânia", "Philips", "Oster"],
    "demo-externos": ["Tramontina", "Vonder", "Husqvarna", "Stihl"],
}

DEMO_IMOVEL_CATEGORIES = [
    {"name": "Sede (Demo)", "slug": "demo-sede"},
    {"name": "Filial (Demo)", "slug": "demo-filial"},
    {"name": "Galpão (Demo)", "slug": "demo-galpao"},
    {"name": "Terreno (Demo)", "slug": "demo-terreno"},
    {"name": "Apartamento (Demo)", "slug": "demo-apartamento"},
    {"name": "Casa (Demo)", "slug": "demo-casa"},
]

# Modelos de nome por categoria — "{brand}" é substituído pela marca sorteada
# (dentro das marcas plausíveis daquela categoria) quando presente, gerando
# variação sem precisar de uma lista gigante estática.
ITEM_TEMPLATES = {
    "demo-informatica": [
        "Notebook {brand}", "Monitor {brand} 24\"", "Desktop {brand}", "Nobreak {brand}",
        "Teclado {brand}", "Mouse {brand}", "Roteador Wi-Fi {brand}", "Switch de Rede {brand}",
        "Impressora Multifuncional {brand}", "Tablet {brand}", "Headset {brand}", "Webcam {brand}",
        "SSD Externo {brand}", "Estabilizador {brand}",
    ],
    "demo-mobiliario": [
        "Cadeira {brand}", "Mesa de Escritório", "Armário de Aço", "Estante de Aço",
        "Poltrona de Recepção", "Mesa de Reunião", "Longarina de Espera", "Sofá de Recepção",
        "Balcão de Atendimento", "Divisória de Ambiente", "Painel Ripado",
    ],
    "demo-eletrodomesticos": [
        "Geladeira {brand}", "Micro-ondas {brand}", "Cafeteira {brand}", "Bebedouro {brand}",
        "Ar-condicionado {brand}", "Ventilador {brand}", "Purificador de Água {brand}",
        "Liquidificador {brand}", "Forno Elétrico {brand}",
    ],
    "demo-ferramentas": [
        "Furadeira {brand}", "Parafusadeira {brand}", "Serra Elétrica {brand}", "Esmerilhadeira {brand}",
        "Compressor de Ar {brand}", "Lixadeira {brand}", "Nível a Laser {brand}", "Chave de Impacto {brand}",
    ],
    "demo-audiovisual": [
        "Projetor {brand}", "Caixa de Som {brand}", "Câmera {brand}", "Microfone {brand}", "TV {brand} 50\"",
        "Mesa de Som {brand}", "Tripé para Câmera", "Rádio Comunicador {brand}",
    ],
    "demo-seguranca": [
        "Câmera de Segurança {brand}", "Extintor de Incêndio", "Detector de Fumaça", "Alarme {brand}",
        "Fechadura Eletrônica {brand}", "Cerca Elétrica {brand}",
    ],
    "demo-veiculos": [
        "Carro de Passeio {brand}", "Caminhonete {brand}", "Van de Transporte {brand}", "Motocicleta {brand}",
    ],
    "demo-copa-cozinha": [
        "Fogão Industrial {brand}", "Forno Combinado {brand}", "Freezer Horizontal {brand}",
        "Máquina de Café {brand}",
    ],
    "demo-externos": [
        "Cortador de Grama {brand}", "Roçadeira {brand}", "Mangueira de Jardim", "Mesa para Área Externa",
    ],
}

STATUS_WEIGHTS = [
    (MovelStatus.IN_USE, 58),
    (MovelStatus.STORED, 18),
    (MovelStatus.MAINTENANCE, 10),
    (MovelStatus.MISSING, 6),
    (MovelStatus.DISCARDED, 8),
]
CONDITION_WEIGHTS = [
    (ItemCondition.EXCELLENT, 25),
    (ItemCondition.GOOD, 45),
    (ItemCondition.FAIR, 22),
    (ItemCondition.POOR, 8),
]

# Usados apenas para variar o "loaned_to" dos empréstimos de demonstração.
DEMO_PEOPLE = [
    "Ana Silva", "Bruno Costa", "Carla Souza", "Diego Almeida", "Elisa Ferreira",
    "Fábio Ramos", "Gabriela Nunes", "Henrique Lima", "Isabela Rocha", "João Pereira",
    "Karina Duarte", "Lucas Martins", "Mariana Gomes", "Nicolas Barros", "Otávio Teixeira",
    "Patrícia Cardozo", "Rafael Andrade", "Sabrina Moreira", "Thiago Batista", "Vitória Campos",
]

IMOVEL_TEMPLATES = [
    {"name": "Sede Administrativa (Demo)", "value": Decimal("850000.00"), "zone": ZonaTipo.URBANA, "category": "demo-sede"},
    {"name": "Escritório Compartilhado (Demo)", "value": Decimal("340000.00"), "zone": ZonaTipo.URBANA, "category": "demo-sede"},
    {"name": "Filial Zona Sul (Demo)", "value": Decimal("610000.00"), "zone": ZonaTipo.URBANA, "category": "demo-filial"},
    {"name": "Filial Zona Norte (Demo)", "value": Decimal("530000.00"), "zone": ZonaTipo.URBANA, "category": "demo-filial"},
    {"name": "Filial Zona Leste (Demo)", "value": Decimal("495000.00"), "zone": ZonaTipo.URBANA, "category": "demo-filial"},
    {"name": "Filial Litoral (Demo)", "value": Decimal("560000.00"), "zone": ZonaTipo.URBANA, "category": "demo-filial"},
    {"name": "Galpão de Estoque (Demo)", "value": Decimal("420000.00"), "zone": ZonaTipo.URBANA, "category": "demo-galpao"},
    {"name": "Galpão Industrial (Demo)", "value": Decimal("610000.00"), "zone": ZonaTipo.URBANA, "category": "demo-galpao"},
    {"name": "Depósito Regional (Demo)", "value": Decimal("275000.00"), "zone": ZonaTipo.RURAL, "category": "demo-galpao"},
    {"name": "Terreno Industrial (Demo)", "value": Decimal("980000.00"), "zone": ZonaTipo.RURAL, "category": "demo-terreno"},
    {"name": "Terreno para Expansão (Demo)", "value": Decimal("505000.00"), "zone": ZonaTipo.RURAL, "category": "demo-terreno"},
    {"name": "Terreno Urbano (Demo)", "value": Decimal("640000.00"), "zone": ZonaTipo.URBANA, "category": "demo-terreno"},
    {"name": "Apartamento Funcional (Demo)", "value": Decimal("380000.00"), "zone": ZonaTipo.URBANA, "category": "demo-apartamento"},
    {"name": "Apartamento para Visitantes (Demo)", "value": Decimal("410000.00"), "zone": ZonaTipo.URBANA, "category": "demo-apartamento"},
    {"name": "Casa de Hóspedes (Demo)", "value": Decimal("590000.00"), "zone": ZonaTipo.RURAL, "category": "demo-casa"},
    {"name": "Sítio Corporativo (Demo)", "value": Decimal("720000.00"), "zone": ZonaTipo.RURAL, "category": "demo-casa"},
]

DEFAULT_IMOVEL_COUNT = len(IMOVEL_TEMPLATES)


def _weighted_choice(rng: random.Random, weighted_options):
    options = [option for option, _weight in weighted_options]
    weights = [weight for _option, weight in weighted_options]
    return rng.choices(options, weights=weights, k=1)[0]


def _shift_color(color: tuple, amount: int) -> tuple:
    return tuple(max(0, min(255, channel + amount)) for channel in color)


def _generate_placeholder_image(label: str, color: tuple) -> ContentFile:
    """Gera uma imagem quadrada simples (cor sólida + rótulo) só pra demonstração —
    evita depender de fotos reais/externas pra exercitar upload e renderização."""
    image = Image.new("RGB", (400, 400), color=color)
    draw = ImageDraw.Draw(image)
    text = label[:24]
    bbox = draw.textbbox((0, 0), text)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((400 - text_w) / 2, (400 - text_h) / 2), text, fill=(255, 255, 255))

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    content_file = ContentFile(buffer.getvalue())
    content_file.content_type = "image/jpeg"
    return content_file


class Command(BaseCommand):
    help = (
        "Popula uma organização de demonstração ('Organização Demo') com categorias, "
        "setores, marcas, localizações, itens (com fotos geradas, valores, empréstimos "
        "e manutenções) e imóveis de exemplo, pra testar visualmente listagens, edição "
        "e o dashboard com dados variados. Todos os membros existentes são vinculados a "
        "essa organização. Use 'clear_demo_data' pra remover tudo de novo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--items", type=int, default=DEFAULT_ITEM_COUNT,
            help=f"Quantidade de bens móveis a gerar (padrão {DEFAULT_ITEM_COUNT}).",
        )
        parser.add_argument(
            "--imoveis", type=int, default=DEFAULT_IMOVEL_COUNT,
            help=f"Quantidade de imóveis a gerar (máx {len(IMOVEL_TEMPLATES)}, padrão {DEFAULT_IMOVEL_COUNT}).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        item_count = max(0, options["items"])
        imovel_count = min(max(0, options["imoveis"]), len(IMOVEL_TEMPLATES))
        rng = random.Random(RNG_SEED)

        organization, org_created = Organization.objects.get_or_create(
            slug=DEMO_ORG_SLUG,
            defaults={
                "name": "Organização Demo",
                "industry": OrganizationIndustry.TECHNOLOGY,
                "size": OrganizationSize.SMALL,
                "primary_goal": OrganizationGoal.FIXED_ASSETS,
            },
        )
        self.stdout.write(self.style.SUCCESS(
            f"{'Criada' if org_created else 'Reaproveitada'} organização: {organization.name}"
        ))

        User = get_user_model()
        users = list(User.objects.all())
        for user in users:
            Membership.objects.get_or_create(
                user=user, organization=organization,
                defaults={"role": MembershipRole.OWNER},
            )
        if users:
            self.stdout.write(f"Vinculados {len(users)} usuário(s) existente(s) como membros.")
        else:
            self.stdout.write(self.style.WARNING(
                "Nenhum usuário encontrado — crie uma conta e rode o comando de novo "
                "pra conseguir acessar a organização demo pela interface."
            ))

        categories_by_slug = {
            c["slug"]: Category.objects.get_or_create(slug=c["slug"], defaults={"name": c["name"]})[0]
            for c in DEMO_CATEGORIES
        }
        sectors_by_slug = {
            s["slug"]: Sector.objects.get_or_create(slug=s["slug"], defaults={"name": s["name"]})[0]
            for s in DEMO_SECTORS
        }
        imovel_categories = {
            c["slug"]: ImovelCategory.objects.get_or_create(slug=c["slug"], defaults={"name": c["name"]})[0]
            for c in DEMO_IMOVEL_CATEGORIES
        }

        all_brand_names = sorted({name for names in BRANDS_BY_CATEGORY.values() for name in names})
        brands_by_name = {
            name: Brand.objects.get_or_create(
                slug=f"demo-{slugify(name)}", defaults={"name": f"{name} (Demo)"},
            )[0]
            for name in all_brand_names
        }

        locations = []
        for sector_data in DEMO_SECTORS:
            sector = sectors_by_slug[sector_data["slug"]]
            for suffix in ("Sala Principal", "Depósito"):
                location, _ = Location.objects.get_or_create(
                    sector=sector, name=f"{suffix} — {sector.name}",
                )
                locations.append(location)

        created_items = 0
        created_loans = 0
        created_maintenances = 0
        today = date.today()

        category_weights = [(c, c["weight"]) for c in DEMO_CATEGORIES]
        sector_weights = [(s, s["weight"]) for s in DEMO_SECTORS]

        for index in range(item_count):
            category_data = _weighted_choice(rng, category_weights)
            category = categories_by_slug[category_data["slug"]]
            sector_data = _weighted_choice(rng, sector_weights)
            sector = sectors_by_slug[sector_data["slug"]]
            category_brand_names = BRANDS_BY_CATEGORY.get(category_data["slug"])
            brand_name = rng.choice(category_brand_names) if category_brand_names else rng.choice(all_brand_names)
            brand = brands_by_name[brand_name]

            templates = ITEM_TEMPLATES[category_data["slug"]]
            template = templates[rng.randrange(len(templates))]
            name = template.format(brand=brand_name) if "{brand}" in template else template

            code = f"DEMO-{index + 1:04d}"
            status = _weighted_choice(rng, STATUS_WEIGHTS)
            condition = _weighted_choice(rng, CONDITION_WEIGHTS)
            location = rng.choice(locations) if rng.random() < 0.5 else None

            item, item_created = Movel.objects.get_or_create(
                organization=organization,
                code=code,
                defaults={
                    "name": name,
                    "description": "Item de demonstração gerado automaticamente.",
                    "category": category,
                    "sector": sector,
                    "location": location,
                    "ownership": AssetOwnership.OWN if rng.random() < 0.85 else AssetOwnership.THIRD_PARTY,
                    "condition": condition,
                    "status": status,
                },
            )
            if not item_created:
                continue

            created_items += 1
            color = _shift_color(category_data["color"], rng.randint(-25, 25))
            image_file = _generate_placeholder_image(name, color)
            spec = MovelSpec(
                movel=item,
                brand=brand,
                model_name=f"Modelo {rng.randint(100, 999)}",
                serial_number=f"SN-DEMO-{index + 1:05d}",
            )
            spec.image.save(f"{code}.jpg", image_file, save=True)

            Acquisition.objects.create(
                item=item,
                value=Decimal(rng.randint(80, 12000)).quantize(Decimal("1.00")),
                purchase_date=today - timedelta(days=rng.randint(15, 720)),
            )

            # ── Manutenção: itens em manutenção sempre ganham um chamado aberto;
            # alguns outros ganham histórico de manutenção já concluída.
            if status == MovelStatus.MAINTENANCE:
                Maintenance.objects.create(
                    item=item,
                    description="Manutenção corretiva de demonstração.",
                    status=rng.choice([MaintenanceStatus.OPEN, MaintenanceStatus.IN_PROGRESS]),
                    started_at=today - timedelta(days=rng.randint(8, 45)),
                    performed_by="Equipe Técnica (Demo)",
                )
                created_maintenances += 1
            elif rng.random() < 0.12:
                started = today - timedelta(days=rng.randint(60, 300))
                Maintenance.objects.create(
                    item=item,
                    description="Manutenção preventiva de demonstração.",
                    status=MaintenanceStatus.DONE,
                    started_at=started,
                    finished_at=started + timedelta(days=rng.randint(1, 10)),
                    cost=Decimal(rng.randint(50, 800)).quantize(Decimal("1.00")),
                    performed_by="Equipe Técnica (Demo)",
                    result="Manutenção concluída sem intercorrências.",
                )
                created_maintenances += 1

            # ── Empréstimos: só faz sentido para itens em uso/guardados.
            if status in (MovelStatus.IN_USE, MovelStatus.STORED) and rng.random() < 0.25:
                loan_kind = rng.random()
                loaned_at = timezone.now() - timedelta(days=rng.randint(20, 200))
                loaned_to = f"{rng.choice(DEMO_PEOPLE)} (Demo)"
                if loan_kind < 0.4:
                    # Devolvido — histórico.
                    expected_return_at = loaned_at + timedelta(days=rng.randint(5, 20))
                    Loan.objects.create(
                        item=item, loaned_to=loaned_to,
                        loaned_at=loaned_at, expected_return=expected_return_at.date(),
                        returned_at=expected_return_at + timedelta(days=rng.randint(0, 5)),
                        status=LoanStatus.RETURNED,
                    )
                elif loan_kind < 0.7:
                    # Ativo, dentro do prazo.
                    Loan.objects.create(
                        item=item, loaned_to=loaned_to,
                        loaned_at=loaned_at, expected_return=today + timedelta(days=rng.randint(3, 30)),
                        status=LoanStatus.ACTIVE,
                    )
                elif loan_kind < 0.85:
                    # Ativo, mas com prazo já vencido (cai no alerta de "atrasados").
                    Loan.objects.create(
                        item=item, loaned_to=loaned_to,
                        loaned_at=loaned_at, expected_return=today - timedelta(days=rng.randint(1, 10)),
                        status=LoanStatus.ACTIVE,
                    )
                else:
                    # Marcado explicitamente como atrasado.
                    Loan.objects.create(
                        item=item, loaned_to=loaned_to,
                        loaned_at=loaned_at, expected_return=today - timedelta(days=rng.randint(1, 15)),
                        status=LoanStatus.OVERDUE,
                    )
                created_loans += 1

        self.stdout.write(self.style.SUCCESS(
            f"Criados {created_items} bem(ns) móvel(is) com foto e valor de aquisição "
            f"({created_loans} com empréstimo, {created_maintenances} com manutenção)."
        ))

        created_imoveis = 0
        for index in range(imovel_count):
            template = IMOVEL_TEMPLATES[index]
            code = f"DEMO-IMV-{index + 1:04d}"
            imovel, imovel_created = Imovel.objects.get_or_create(
                organization=organization,
                code=code,
                defaults={
                    "name": template["name"],
                    "description": "Imóvel de demonstração gerado automaticamente.",
                    "category": imovel_categories[template["category"]],
                    "ownership": AssetOwnership.OWN,
                    "condition": _weighted_choice(rng, CONDITION_WEIGHTS),
                    "zone": template["zone"],
                    "cartorio_situacao": rng.choice(list(CartorioSituacao)),
                    "total_area": Decimal(rng.randint(80, 2000)),
                    "built_area": Decimal(rng.randint(50, 1500)),
                },
            )
            if not imovel_created:
                continue

            created_imoveis += 1
            Acquisition.objects.create(
                item=imovel, value=template["value"], purchase_date=today - timedelta(days=rng.randint(180, 1500)),
            )

        self.stdout.write(self.style.SUCCESS(f"Criado(s) {created_imoveis} imóvel(is) de demonstração."))
        self.stdout.write(self.style.SUCCESS(
            "Pronto! Faça login com um usuário existente, troque para 'Organização Demo' "
            "no seletor de organizações e veja os dados de exemplo."
        ))
