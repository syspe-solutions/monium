from apps.organizations.models import OrganizationIndustry

INDUSTRY_SUGGESTIONS = {
    OrganizationIndustry.TECHNOLOGY: {
        "categories": ["Equipamentos de Informática", "Equipamentos Audiovisuais", "Telecomunicações", "Mobiliário de Escritório"],
        "sectors": ["Tecnologia da Informação", "Suporte Técnico", "Desenvolvimento", "Administrativo"],
    },
    OrganizationIndustry.EDUCATION: {
        "categories": ["Equipamentos de Informática", "Mobiliário de Escritório", "Material Gráfico e Comunicação", "Equipamentos Audiovisuais"],
        "sectors": ["Coordenação Pedagógica", "Secretaria Acadêmica", "Biblioteca", "Laboratório"],
    },
    OrganizationIndustry.HEALTHCARE: {
        "categories": ["Equipamentos de Informática", "Equipamentos de Segurança", "Mobiliário de Escritório", "Ferramentas e Manutenção"],
        "sectors": ["Recepção", "Enfermagem", "Administrativo", "Almoxarifado"],
    },
    OrganizationIndustry.RETAIL: {
        "categories": ["Equipamentos de Informática", "Mobiliário de Apoio", "Material Gráfico e Comunicação", "Equipamentos de Segurança"],
        "sectors": ["Loja", "Estoque", "Financeiro", "Administrativo"],
    },
    OrganizationIndustry.MANUFACTURING: {
        "categories": ["Ferramentas e Manutenção", "Equipamentos de Segurança", "Equipamentos de Informática", "Telecomunicações"],
        "sectors": ["Produção", "Manutenção", "Almoxarifado", "Qualidade"],
    },
    OrganizationIndustry.SERVICES: {
        "categories": ["Equipamentos de Informática", "Mobiliário de Escritório", "Telecomunicações"],
        "sectors": ["Comercial", "Operações", "Administrativo", "Financeiro"],
    },
    OrganizationIndustry.CONSTRUCTION: {
        "categories": ["Ferramentas e Manutenção", "Equipamentos de Segurança", "Equipamentos de Informática"],
        "sectors": ["Obra", "Engenharia", "Almoxarifado", "Administrativo"],
    },
    OrganizationIndustry.PUBLIC_SECTOR: {
        "categories": ["Mobiliário de Escritório", "Equipamentos de Informática", "Material Gráfico e Comunicação", "Telecomunicações"],
        "sectors": ["Protocolo", "Recursos Humanos", "Financeiro", "Administrativo"],
    },
    OrganizationIndustry.OTHER: {
        "categories": ["Equipamentos de Informática", "Mobiliário de Escritório"],
        "sectors": ["Administrativo"],
    },
}
