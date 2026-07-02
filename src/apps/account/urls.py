from django.urls import path

from apps.account.views.auth import (
    DeactivateAccount,
    RecoveryCompleteView,
    RecoveryConfirmView,
    RecoveryDoneView,
    RecoveryView,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
)
from apps.account.views.avatar_redirect_view import AvatarRedirectView
from apps.account.views.upload_avatar_view import UploadAvatarView
from apps.account.views.user_delete_view import UserDeleteView
from apps.account.views.user_profile_update_view import UserProfileUpdateView

app_name = "account"

urlpatterns = [
    # ... (login paths)
    path("login/", UserLoginView.as_view(), name="login"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("logout/", UserLogoutView.as_view(), name="logout"),

    # Profile
    path('profile/delete', UserDeleteView.as_view(), name='profile_delete'),
    path('profile/edit', UserProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/avatar', UploadAvatarView.as_view(), name='upload_avatar'),
    path('profile/avatar/<uuid:user_id>/', AvatarRedirectView.as_view(), name='avatar_view'),
    path("deactivate/", DeactivateAccount.as_view(), name="profile_deactivate"),

    # Recovery
    path("recovery/", RecoveryView.as_view(), name="recovery"),
    path("recovery/done/", RecoveryDoneView.as_view(), name="password_reset_done"),
    path(
        "recovery/confirm/<uidb64>/<token>/",
        RecoveryConfirmView.as_view(),
        name="recovery_confirm",
    ),
    path("recovery/complete/", RecoveryCompleteView.as_view(),
         name="password_reset_complete"),
]
