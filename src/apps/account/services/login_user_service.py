from django.contrib.auth import authenticate, get_user_model

from apps.account.dtos.login_result_dto import LoginResultDTO
from apps.account.dtos.login_user_dto import LoginUserDTO

User = get_user_model()


class LoginUserService:

    @staticmethod
    def execute(request, dto: LoginUserDTO) -> LoginResultDTO:

        user = authenticate(
            request=request,
            username=dto.username,
            password=dto.password
        )

        if not user:
            return LoginResultDTO(
                success=False,
                error_code="invalid_credentials"
            )

        if not user.is_active:
            return LoginResultDTO(
                success=False,
                error_code="inactive_user"
            )

        return LoginResultDTO(success=True, user=user)
