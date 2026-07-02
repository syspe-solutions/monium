try:
    from str2bool import str2bool
except ImportError:
    def str2bool(v):
        return v.lower() in ('true', '1', 'yes', 'on')


class EnvConverter:
    @staticmethod
    def str_to_bool(value, default=False):
        if value is None:
            return default
        try:
            return str2bool(value)
        except Exception:
            return default
