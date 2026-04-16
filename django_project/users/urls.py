from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from users import views

app_name = "users"

urlpatterns = [
    path(
        "ping",
        views.PingView.as_view(),
        name="ping",
    ),
    path(
        "registration",
        views.RegistrationView.as_view(),
        name="registration",
    ),
    path(
        "login",
        views.LoginView.as_view(),
        name="login",
    ),
    path(
        "logout",
        views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "<int:user_id>/profile",
        views.ProfileView.as_view(),
        name="profile",
    ),
    path(
        "admin/load_fixtures",
        views.export_fixtures,
        name="load_fixtures",
    ),
    # # Тестовый url для входа в админку
    # path(
    #     "admin/login_to_admin",
    #     views.LoginToAdminView.as_view()  ,  # noqa: ERA001
    #     name="load_fixtures",  # noqa: ERA001
    # ),
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
        views.AuthSteamCompleteView.as_view(),
        name="auth_steam_complete",
    ),
]
