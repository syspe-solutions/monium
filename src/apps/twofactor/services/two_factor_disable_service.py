from apps.twofactor.models import TwoFactorDevice


class TwoFactorDisableService:
    @staticmethod
    def disable(user) -> bool:
        deleted_count, _details = TwoFactorDevice.objects.filter(user=user).delete()
        return deleted_count > 0
