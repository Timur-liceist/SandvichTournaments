from tournaments.models import TournamentModel
from users.models import UserModel


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
