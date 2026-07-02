
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as translate

from apps.account.dtos.create_user_dto import CreateUserDTO
from apps.account.models import User


class CreateUserService:
    @staticmethod
    @transaction.atomic
    def execute(dto: CreateUserDTO) -> User:
        try:
            user = User.objects.create_user(
                username=dto.username,
                email=dto.email,
                password=dto.password
            )
        except IntegrityError:
            return User.objects.get(username=dto.username)

        return user
