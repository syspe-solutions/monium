from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


class EncryptedCharField(models.CharField):
    """CharField persistido criptografado (Fernet: AES-128-CBC + HMAC) e decriptado
    de forma transparente ao ler do banco.

    Não é hash: hashing é irreversível, e a senha SMTP precisa voltar em texto puro
    para autenticar no servidor de e-mail — por isso a proteção aqui é criptografia
    simétrica reversível, com a chave em settings.ENCRYPTION_KEY (DJANGO_ENCRYPTION_KEY
    no .env, fora do banco de dados)."""

    def get_internal_type(self):
        return "TextField"

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if not value:
            return value
        return Fernet(settings.ENCRYPTION_KEY).encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return Fernet(settings.ENCRYPTION_KEY).decrypt(value.encode()).decode()
        except InvalidToken:
            return value
