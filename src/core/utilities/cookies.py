from core.utilities.converters import EnvConverter
from core.utilities.enviroment import EnvReader


class CookieConfig:
    def __init__(self, prefix, is_dev_mode):
        self.prefix = prefix
        self.is_dev_mode = is_dev_mode

    def build(self):
        if self.is_dev_mode:
            return {
                f'{self.prefix}_SECURE': False,
                f'{self.prefix}_HTTPONLY': False,
                f'{self.prefix}_SAMESITE': 'Lax',
                f'{self.prefix}_DOMAIN': None,
                f'{self.prefix}_PATH': '/',
            }

        return {
            f'{self.prefix}_SECURE': EnvConverter.str_to_bool(
                EnvReader.get(f'DJANGO_{self.prefix}_SECURE', 'True')
            ),
            f'{self.prefix}_HTTPONLY': EnvConverter.str_to_bool(
                EnvReader.get(f'DJANGO_{self.prefix}_HTTPONLY', 'True')
            ),
            f'{self.prefix}_SAMESITE': EnvReader.get(
                f'DJANGO_{self.prefix}_SAMESITE', 'Lax'
            ),
            f'{self.prefix}_DOMAIN': EnvReader.get(
                f'DJANGO_{self.prefix}_DOMAIN', None
            ),
            f'{self.prefix}_PATH': EnvReader.get(
                f'DJANGO_{self.prefix}_PATH', '/'
            ),
        }
