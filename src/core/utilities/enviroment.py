import os


class EnvReader:
    @staticmethod
    def get(key, default=None, converter=None):
        value = os.environ.get(key, default)
        return converter(value) if converter else value

    @staticmethod
    def get_list(key, default=None):
        if default is None:
            default = []
        value = os.environ.get(key, '')
        return [item.strip() for item in value.split(',') if item.strip()] if value else default
