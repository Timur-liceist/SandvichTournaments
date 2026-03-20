from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from users.views import (
    AuthSteamCompleteView,
    LoginView,
    LogoutView,
    PingView,
    ProfileView,
    RegistrationView,
    ToAdminView,
    ToTestUserView,
    export_fixtures,
)

app_name = "users"

urlpatterns = [
    path(
        "ping",
        PingView.as_view(),
        name="ping",
    ),
    path(
        "to_test_user",
        ToTestUserView.as_view(),
        name="to_admin",
    ),
    path(
        "to_admin",
        ToAdminView.as_view(),
        name="to_admin",
    ),
    path(
        "registration",
        RegistrationView.as_view(),
        name="registration",
    ),
    path(
        "login",
        LoginView.as_view(),
        name="login",
    ),
    path(
        "logout",
        LogoutView.as_view(),
        name="logout",
    ),
    path(
        "<int:user_id>/profile",
        ProfileView.as_view(),
        name="profile",
    ),
    path(
        "admin/load_fixtures",
        export_fixtures,
        name="load_fixtures",
    ),
    path(
        "not_logined",
        TemplateView.as_view(
            template_name="includes/error.html",
            extra_context={
                "error_message": "Вы не авторизованы",
            },
        ),
        name="not_logined",
    ),
    path(
        "not_public_profile",
        TemplateView.as_view(
            template_name="includes/error.html",
            extra_context={
                "error_message": "Профиль приватный",
            },
        ),
        name="not_public_profile",
    ),
    path(
        "need_auth_steam",
        TemplateView.as_view(
            template_name="includes/error.html",
            extra_context={
                "error_message": "Пожалуйста авторизуйтесь через Steam",
                "href_link": reverse_lazy("social:begin", args=["steam"]),
                "button_text": "Войти через Steam",
            },
        ),
        name="need_auth_steam",
    ),
    path(
        "auth/steam/<str:steam_id>/complete",
        AuthSteamCompleteView.as_view(),
        name="auth_steam_complete",
    ),
]
