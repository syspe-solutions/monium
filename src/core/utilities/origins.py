from core.utilities.enviroment import EnvReader


class CorsOrigins:
    DEFAULT_DEV_ORIGINS = [
        'http://127.0.0.1',
        'http://localhost',
        'http://127.0.0.1:6085',
        'http://localhost:6085',
        'https://127.0.0.1',
        'https://localhost',
        'https://127.0.0.1:6085',
        'https://localhost:6085',
    ]

    def __init__(self, is_dev_mode):
        self.is_dev_mode = is_dev_mode

    def allowed_hosts(self):
        return EnvReader.get_list(
            'DJANGO_ALLOWED_HOSTS',
            ['*'] if self.is_dev_mode else ['localhost', '127.0.0.1']
        )

    def csrf_trusted_origins(self, allow_all):
        if allow_all:
            return ['http://*', 'https://*']
        return EnvReader.get_list(
            'DJANGO_CSRF_TRUSTED_ORIGINS',
            self.DEFAULT_DEV_ORIGINS
        )
