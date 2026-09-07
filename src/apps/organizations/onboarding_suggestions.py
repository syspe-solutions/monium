from apps.organizations.models import OrganizationIndustry

INDUSTRY_SUGGESTIONS = {
    OrganizationIndustry.TECHNOLOGY: {
        "categories": [
            "Equipamentos de Informática", "Notebooks e Laptops", "Servidores e Armazenamento",
            "Periféricos de Informática", "Impressoras e Multifuncionais", "Redes e Telecomunicações",
            "Equipamentos de Telefonia Móvel", "Tablets e Dispositivos Móveis", "Equipamentos Audiovisuais",
            "Sistemas de Monitoramento (CFTV)", "Mobiliário de Escritório",
        ],
        "sectors": ["Tecnologia da Informação", "Suporte Técnico", "Desenvolvimento", "Administrativo"],
    },
    OrganizationIndustry.EDUCATION: {
        "categories": [
            "Equipamentos de Informática", "Notebooks e Laptops", "Mobiliário de Escritório",
            "Material Gráfico e Comunicação", "Equipamentos Audiovisuais", "Equipamentos de Som e Iluminação",
            "Acervo Bibliográfico", "Instrumentos Musicais", "Equipamentos Esportivos",
            "Equipamentos de Academia", "Impressoras e Multifuncionais",
        ],
        "sectors": ["Coordenação Pedagógica", "Secretaria Acadêmica", "Biblioteca", "Laboratório"],
    },
    OrganizationIndustry.HEALTHCARE: {
        "categories": [
            "Equipamentos de Informática", "Equipamentos Médicos e Hospitalares", "Equipamentos Laboratoriais",
            "Equipamentos Odontológicos", "Equipamentos de Segurança", "Equipamentos de Refrigeração",
            "Materiais de Limpeza e Higiene", "Equipamentos de Proteção Individual",
            "Mobiliário de Escritório", "Ferramentas e Manutenção",
        ],
        "sectors": ["Recepção", "Enfermagem", "Administrativo", "Almoxarifado"],
    },
    OrganizationIndustry.RETAIL: {
        "categories": [
            "Equipamentos de Informática", "Mobiliário de Apoio", "Material Gráfico e Comunicação",
            "Sinalização e Placas", "Equipamentos de Segurança", "Sistemas de Monitoramento (CFTV)",
            "Equipamentos de Refrigeração", "Utensílios de Copa e Cozinha", "Impressoras e Multifuncionais",
        ],
        "sectors": ["Loja", "Estoque", "Financeiro", "Administrativo"],
    },
    OrganizationIndustry.MANUFACTURING: {
        "categories": [
            "Máquinas e Equipamentos Industriais", "Ferramentas e Manutenção", "Equipamentos de Segurança",
            "Equipamentos de Proteção Individual", "Equipamentos de Automação e Controle",
            "Instrumentos de Medição e Calibração", "Geradores e Equipamentos de Energia",
            "Equipamentos de Transporte Interno", "Equipamentos de Informática", "Redes e Telecomunicações",
        ],
        "sectors": ["Produção", "Manutenção", "Almoxarifado", "Qualidade"],
    },
    OrganizationIndustry.SERVICES: {
        "categories": [
            "Equipamentos de Informática", "Notebooks e Laptops", "Mobiliário de Escritório",
            "Redes e Telecomunicações", "Impressoras e Multifuncionais", "Veículos Leves",
        ],
        "sectors": ["Comercial", "Operações", "Administrativo", "Financeiro"],
    },
    OrganizationIndustry.CONSTRUCTION: {
        "categories": [
            "Ferramentas e Manutenção", "Equipamentos de Segurança", "Equipamentos de Proteção Individual",
            "Equipamentos de Construção Civil", "Veículos Pesados e Utilitários",
            "Geradores e Equipamentos de Energia", "Contêineres e Estruturas Modulares",
            "Equipamentos de Informática",
        ],
        "sectors": ["Obra", "Engenharia", "Almoxarifado", "Administrativo"],
    },
    OrganizationIndustry.PUBLIC_SECTOR: {
        "categories": [
            "Mobiliário de Escritório", "Armários e Arquivos", "Equipamentos de Informática",
            "Material Gráfico e Comunicação", "Redes e Telecomunicações", "Impressoras e Multifuncionais",
            "Sinalização e Placas", "Veículos Leves",
        ],
        "sectors": ["Protocolo", "Recursos Humanos", "Financeiro", "Administrativo"],
    },
    OrganizationIndustry.OTHER: {
        "categories": [
            "Equipamentos de Informática", "Mobiliário de Escritório", "Ferramentas e Manutenção",
            "Veículos Leves",
        ],
        "sectors": ["Administrativo"],
    },
}
