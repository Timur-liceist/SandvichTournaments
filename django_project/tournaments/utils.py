import requests
from django.conf import settings
from users.models import UserModel

from tournaments.models import TournamentModel


def is_owner_tournament(
    tournament_id=None,
    user_id=None,
    user=None,
    tournament=None,
):
    if not ((tournament or tournament_id) and (user_id or user)):
        error_message = "Missing agrument tournament or user"
        raise TypeError(error_message)

    if tournament_id:
        tournament = TournamentModel.objects.filter(id=tournament_id).first()

    if user_id:
        user = UserModel.objects.filter(id=user_id).first()

    return user == tournament.owner or user.is_superuser


# Функция для получения всех id участников турнира
def get_all_id_members_tournament(tournament_id=None, tournament=None):
    if not tournament_id and not tournament:
        error_message = "Need at least argument tournament_id or tournament"
        raise TypeError(error_message)

    if tournament_id:
        tournament = TournamentModel.objects.filter(id=tournament_id).first()

    if not tournament:
        error_message = "Tournament not found"
        raise TypeError(error_message)

    all_id_members_tournament = []

    for team in tournament.team_members.all():
        all_id_members_tournament.extend(
            team.members_by_team.all().values_list(
                "user__id",
                flat=True,
            ),
        )

    return all_id_members_tournament


# Функция для выдачи роли(DISCORD_ROLE_MEMBER_ID)
# в определённом Дискорд сервере(DISCORD_GUILD_ID)
def give_role(discord_user_id):
    url = f"https://discord.com/api/v10/guilds/\
        {settings.DISCORD_GUILD_ID}/members/{discord_user_id}/roles/{settings.DISCORD_ROLE_MEMBER_ID}"
    print(f"url: {url}")

    headers = {
        "Authorization": f"Bot {settings.DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.put(url, headers=headers, timeout=5)

        # Принудительно задаем кодировку UTF-8 для ответа
        response.encoding = "utf-8"

        if response.status_code == 204:
            print("Успех: Роль выдана!")
        else:
            # Печатаем только текстовое содержимое, избегая печати самого объекта response
            error_text = response.text

            print(f"Статус: {response.status_code}")
            print(f"Ответ сервера: {error_text}")

            # Дополнительная подсказка для частых ошибок
            if response.status_code == 401:
                print("-> Проверьте токен (он неверен или сброшен).")
            elif response.status_code == 403:
                print("-> Проверьте права бота и иерархию ролей.")
            elif response.status_code == 404:
                print("-> Проверьте ID пользователя, сервера или роли.")

    except UnicodeEncodeError as e:
        # Если ошибка кодировки всё же возникла при печати
        print(f"Ошибка кодировки при выводе: {e}")
        print(
            "Попробуйте запустить скрипт в терминале с поддержкой UTF-8 (PowerShell или новый Terminal Windows)."
        )
    except Exception as e:
        print(f"Критическая ошибка соединения: {e}")
