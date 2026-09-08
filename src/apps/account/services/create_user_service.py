
from django.db import IntegrityError, transaction

from apps.account.dtos.create_user_dto import CreateUserDTO
from apps.account.models import User


class CreateUserService:
    @staticmethod
    @transaction.atomic
    def execute(dto: CreateUserDTO) -> User:
        first_name, _sep, last_name = dto.full_name.strip().partition(' ')

        try:
            user = User.objects.create_user(
                username=dto.username,
                email=dto.email,
                password=dto.password,
                first_name=first_name,
                last_name=last_name,
            )
        except IntegrityError:
            return User.objects.get(username=dto.username)

        return user
