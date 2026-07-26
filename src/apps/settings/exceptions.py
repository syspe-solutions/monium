class EmailNotConfiguredError(Exception):
    """Levantada ao tentar enviar e-mail sem um servidor SMTP cadastrado e ativado
    em Configurações > E-mail. Não existe mais fallback para variáveis de ambiente."""
