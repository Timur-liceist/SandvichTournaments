from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.core.management import call_command
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from users.forms import LoginForm, ProfileForm, RegistrationForm
from users.models import UserModel


class PingView(View):
    def get(self, request):
        return render(
            request,
            "users/ping.html",
        )


# Регистрация(дополнение данных кроме steam_id) пользователя в системе
class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()

        # Проверка, есть ли steam_id в сессии
        if request.session.get("steam_id") is None:
            return redirect("forbidden")

        context = {
            "form": form,
        }
        return render(
            request,
            "users/registration.html",
            context=context,
        )

    def post(self, request):
        form = RegistrationForm(request.POST)

        if form.is_valid():
            new_user = form.save(commit=False)

            if request.session.get("steam_id") is None:
                return redirect("forbidden")

            new_user.steamid64 = request.session.get("steam_id")

            new_user.set_password(new_user.password)
            new_user.is_active = True

            new_user.save()

            return redirect("news:general_news")

        context = {
            "form": form,
        }
        return render(
            request,
            "users/registration.html",
            context=context,
        )


class LoginView(View):
    def get(self, request):
        form = LoginForm()

        context = {
            "form": form,
        }

        return render(
            request,
            "users/login.html",
            context=context,
        )

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            email_or_username = form.cleaned_data["email_or_username"]
            password = form.cleaned_data["password"]

            query_find_user = Q(username=email_or_username) | Q(
                email=email_or_username,
            )
            user = UserModel.objects.filter(query_find_user).first()

            if user is None:
                form.add_error(None, "Неверные данные для входа")
                return render(
                    request,
                    "users/login.html",
                    context={"form": form},
                )

            if check_password(password, user.password):
                user.is_active = True
                login(request, user)
                return redirect(
                    "news:general_news",
                )

            form.add_error(None, "Неверные данные для входа")

        context = {
            "form": form,
        }
        return render(
            request,
            "users/login.html",
            context=context,
        )


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect(
            "news:general_news",
        )


class ProfileView(View):
    def get(self, request, user_id):
        user_for_update = get_object_or_404(UserModel, id=user_id)
        is_owner_profile = False

        if request.user == user_for_update or request.user.is_superuser:
            is_owner_profile = True

        if not is_owner_profile and not user_for_update.is_public_profile:
            return redirect("users:not_public_profile")

        form = ProfileForm(
            instance=user_for_update,
        )

        if not is_owner_profile:
            form.fields.pop("email")

        context = {
            "form": form,
            "is_owner_profile": is_owner_profile,
            "steamid64_of_user": user_for_update.steamid64,
        }
        return render(
            request,
            "users/profile.html",
            context=context,
        )

    def post(self, request, user_id):
        if not request.user.is_authenticated:
            return redirect("users:not_logined")

        user_for_update = get_object_or_404(UserModel, id=user_id)

        if request.user != user_for_update and not request.user.is_superuser:
            return redirect("forbidden")

        form = ProfileForm(
            request.POST,
            instance=user_for_update,
        )

        if form.is_valid():
            user = form.save()
            user.save()

            return redirect("users:profile", user_id=user.id)

        context = {
            "form": form,
            "is_owner": True,
            "steamid64_of_user": user_for_update.steamid64,
        }
        return render(
            request,
            "users/profile.html",
            context=context,
        )


class AuthSteamCompleteView(View):
    def get(self, request, steam_id):
        user = UserModel.objects.filter(steamid64=steam_id).first()

        request.session["steam_id"] = steam_id

        if user is not None:
            login(request, user)

        return redirect("users:registration")


# # Тестовый view для входа в админку
# class LoginToAdminView(View):
#     def get(self, request):
#         user_admin = UserModel.objects.filter(username="Rusik").first()  # noqa: E501, ERA001
#         login(
#             request,
#             user_admin,
#             backend="django.contrib.auth.backends.ModelBackend",  # noqa: E501, ERA001
#         )  # noqa: ERA001, RUF100
#         return redirect("homepage")  # noqa: ERA001


def export_fixtures(request):
    if not request.user.is_superuser:
        return redirect("forbidden")
    # Создаем HTTP ответ с типом контента JSON
    response = HttpResponse(content_type="application/json")
    # Указываем браузеру, что это файл для скачивания
    response["Content-Disposition"] = (
        'attachment; filename="all_fixtures.json"'
    )

    # Вызываем команду dumpdata и пишем результат прямо в response
    # ещё exclude=['auth.permission', 'contenttypes']
    # можно добавить, чтобы убрать лишнее
    call_command(
        "dumpdata",
        stdout=response,
    )

    return response
