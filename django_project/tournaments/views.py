from django import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from teams.models import MemberModel

from tournaments.forms import (
    BattleForm,
    RequestTeamTournamentForm,
    TournamentCreateForm,
    TournamentNewsForm,
)
from tournaments.models import (
    BattleModel,
    RequestTeamForTournamentModel,
    TournamentModel,
    TournamentNewsModel,
)
from tournaments.utils import (
    is_owner_tournament,
    get_all_id_members_tournament,
)


class TournamentCreateView(LoginRequiredMixin, views.View):
    def get(self, request):
        if not request.user.is_superuser:
            return redirect("forbidden")

        form = TournamentCreateForm()

        context = {
            "form": form,
        }

        return render(
            request,
            "tournaments/create_tournament.html",
            context=context,
        )

    def post(self, request):
        form = TournamentCreateForm(request.POST)

        if form.is_valid():
            tournament = form.save(commit=False)

            tournament.owner = request.user
            tournament.save()

            # Сразу делаем создателя турнира судьёй
            tournament.judges.add(request.user.id)
            tournament.save()

        return redirect("tournaments:all_tournaments")


class AllTournamentsView(LoginRequiredMixin, views.View):
    def get(self, request):
        tournaments = TournamentModel.objects.select_related(
            "owner",
        ).all()

        return render(
            request=request,
            template_name="tournaments/all_tournaments.html",
            context={
                "tournaments": tournaments,
            },
        )


class SendRequestToTournamentView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id):
        form = RequestTeamTournamentForm()
        form.set_team_selecting(leader_user=request.user)

        tournament = TournamentModel.objects.filter(
            id=tournament_id,
        ).first()

        if tournament.is_closed_for_requests:
            return redirect("tournaments:tournament_reg_is_closed")

        context = {
            "form": form,
        }

        return render(
            request=request,
            context=context,
            template_name="tournaments/send_request_team_tournament.html",
        )

    def post(self, request, tournament_id):
        template_name = "tournaments/send_request_team_tournament.html"

        form = RequestTeamTournamentForm(request.POST)

        if form.is_valid():
            tournament = TournamentModel.objects.filter(
                id=tournament_id,
            ).first()

            if tournament.is_closed_for_requests:
                return redirect("tournaments:tournament_reg_is_closed")

            request_team_tournament = (
                RequestTeamForTournamentModel.objects.filter(
                    team_id=form.cleaned_data["team"].id,
                    tournament_id=tournament.id,
                ).first()
            )

            if request_team_tournament:  # noqa: SIM102
                if request_team_tournament.status in ["pending", "accepted"]:
                    form.add_error(
                        None,
                        "Вы уже послали заявку\
                        и она ожидает ответа, или уже принята",
                    )
                    context = {
                        "form": form,
                    }
                    return render(
                        request=request,
                        context=context,
                        template_name=template_name,
                    )

            # Проверка на то что один из участников команды, уже участвует
            all_id_members_tournament = get_all_id_members_tournament(
                tournament=tournament,
            )

            for member_of_team in form.cleaned_data[
                "team"
            ].members_by_team.all():
                if member_of_team.user_id in all_id_members_tournament:
                    form.add_error(
                        None,
                        f"Сокомандник {member_of_team.user} уже состоит в \
                            другой команде на этом турнире",
                    )
                    context = {
                        "form": form,
                    }
                    return render(
                        request=request,
                        context=context,
                        template_name=template_name,
                    )

            request_team_tournament = RequestTeamForTournamentModel(
                team=form.cleaned_data["team"],
                tournament_id=tournament.id,
            )
            request_team_tournament = request_team_tournament.save()

            return redirect("tournaments:all_tournaments")

        return redirect("tournaments:user_all_request_team_tournament")


class UserAllRequestTeamTournament(LoginRequiredMixin, views.View):
    def get(self, request):
        team_ids = MemberModel.objects.filter(
            user=request.user,
        ).values_list(
            "team_id",
            flat=True,
        )
        requests_team_tournament = (
            RequestTeamForTournamentModel.objects.filter(
                team_id__in=team_ids,
            ).select_related(
                "tournament",
            )
        )
        context = {
            "requests_team_tournament": requests_team_tournament,
        }

        return render(
            request=request,
            context=context,
            template_name="tournaments/user_all_request_team_tournament.html",
        )


class ManageTournamentBattles(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id):
        battles = BattleModel.objects.filter(
            tournament_id=tournament_id,
        )
        context = {
            "battles": battles,
            "tournament_id": tournament_id,
            "is_owner_tournament": is_owner_tournament(
                tournament_id=tournament_id,
                user=request.user,
            ),
        }

        return render(
            request=request,
            context=context,
            template_name="tournaments/manage_tournament_battles.html",
        )


class CreateBattleView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id):
        tournament = (
            TournamentModel.objects.filter(
                id=tournament_id,
            )
            .prefetch_related(
                "judges",
            )
            .first()
        )

        is_owner = is_owner_tournament(
            tournament=tournament,
            user=request.user,
        )
        if not is_owner:
            return redirect("forbidden")

        form = BattleForm()

        form.fields.pop("status", None)

        form.set_team_selecting(
            teams_by_tournament=tournament.team_members,
            judges_by_tournament=tournament.judges,
        )
        context = {
            "form": form,
            "is_owner_tournament": is_owner,
        }

        return render(
            request=request,
            context=context,
            template_name="tournaments/edit_battle.html",
        )

    def post(self, request, tournament_id):
        is_owner = is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        )
        if not is_owner:
            return redirect("forbidden")

        form = BattleForm(request.POST)
        form.fields.pop("status", None)

        if form.is_valid():
            new_battle = form.save(commit=False)

            new_battle.tournament_id = tournament_id
            new_battle.save()

            return redirect(
                "tournaments:manage_tournament_battles",
                tournament_id=tournament_id,
            )
        context = {
            "form": form,
            "is_owner": is_owner,
        }
        return render(
            request=request,
            context=context,
            template_name="tournaments/edit_battle.html",
        )


class EditBattleView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id, battle_id):
        is_owner = is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        )
        if not is_owner:
            return redirect("forbidden")

        battle = BattleModel.objects.filter(
            id=battle_id,
        ).first()

        form = BattleForm(instance=battle)

        context = {
            "form": form,
        }

        return render(
            request=request,
            template_name="tournaments/edit_battle.html",
            context=context,
        )

    def post(self, request, tournament_id, battle_id):
        is_owner = is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        )
        if not is_owner:
            return redirect("forbidden")

        battle = BattleModel.objects.filter(
            id=battle_id,
        ).first()

        form = BattleForm(request.POST, instance=battle)

        if form.is_valid():
            form.save()

        return redirect(
            "tournaments:manage_tournament_battles",
            tournament_id=tournament_id,
        )


class DeleteBattleView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id, battle_id):
        is_owner = is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        )
        if not is_owner:
            return redirect("forbidden")

        BattleModel.objects.filter(
            id=battle_id,
        ).delete()

        return redirect(
            "tournaments:manage_tournament_battles",
            tournament_id=tournament_id,
        )


class ManageBattleView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id):
        battles_by_tournament = (
            BattleModel.objects.filter(
                tournament__id=tournament_id,
            )
            .select_related(
                "first_team",
            )
            .select_related(
                "second_team",
            )
            .select_related(
                "judge",
            )
            .all()
        )

        tournament = (
            TournamentModel.objects.filter(
                id=tournament_id,
            )
            .only(
                "owner",
            )
            .select_related(
                "owner",
            )
            .first()
        )

        context = {
            "battles": battles_by_tournament,
            "owner_tournament": tournament.owner,
            "tournament_id": tournament_id,
            "is_owner_tournament": is_owner_tournament(
                tournament=tournament,
                user=request.user,
            ),
        }
        return render(
            request=request,
            template_name="tournaments/manage_battles.html",
            context=context,
        )


class ManageTornamentRequests(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id, status_filter):
        all_team_member_requests = (
            RequestTeamForTournamentModel.objects.filter(
                tournament__id=tournament_id,
            )
            .select_related("team")
            .order_by("-created_at")
        )

        if status_filter != "all":
            all_team_member_requests = all_team_member_requests.filter(
                status=status_filter,
            )

        context = {
            "all_team_member_requests": all_team_member_requests,
            "is_owner_tournament": is_owner_tournament(
                tournament_id=tournament_id,
                user=request.user,
            ),
            "tournament_id": tournament_id,
        }
        return render(
            request=request,
            context=context,
            template_name="tournaments/manage_tournament_requests.html",
        )


class RejectTournamentRequest(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id, tournament_request_id):
        if not is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        ):
            return redirect("forbidden")

        request_team_tournament = RequestTeamForTournamentModel.objects.filter(
            id=tournament_request_id,
        ).first()

        if request_team_tournament.status != "pending":
            return redirect("forbidden")

        request_team_tournament.status = "rejected"
        request_team_tournament.save()

        data = {
            "status": "Rejected",
        }

        return JsonResponse(
            data,
            safe=False,
            status=200,
        )


class AcceptTournamentRequest(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id, tournament_request_id):
        if not is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        ):
            return redirect("forbidden")

        request_team_tournament = (
            RequestTeamForTournamentModel.objects.filter(
                id=tournament_request_id,
            )
            .select_related("team")
            .first()
        )

        if request_team_tournament.status != "pending":
            return redirect("forbidden")

        tournament = (
            TournamentModel.objects.filter(
                id=tournament_id,
            )
            .prefetch_related("team_members")
            .first()
        )

        tournament.team_members.add(request_team_tournament.team)
        tournament.save()

        request_team_tournament.status = "accepted"
        request_team_tournament.save()

        data = {
            "status": "Accepted",
        }

        return JsonResponse(
            data,
            safe=False,
            status=200,
        )


class AllTournamentNewsView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id):
        tournament_news = TournamentNewsModel.objects.select_related(
            "author",
        ).filter(
            tournament__id=tournament_id,
        )

        context = {
            "tournament_news": tournament_news,
            "tournament_id": tournament_id,
            "is_owner_tournament": is_owner_tournament(
                tournament_id=tournament_id,
                user=request.user,
            ),
        }

        return render(
            request,
            "tournaments/tournament_news.html",
            context=context,
        )


class CreateTournamentNewsView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id):
        if not request.user.is_authenticated:
            return redirect("users:not_logined")

        if not is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        ):
            return redirect("forbidden")

        form = TournamentNewsForm()

        context = {
            "form": form,
        }

        return render(
            request,
            "news/create_news.html",
            context=context,
        )

    def post(self, request, tournament_id):
        if not request.user.is_authenticated:
            return redirect("users:not_logined")

        if not is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        ):
            return redirect("forbidden")

        form = TournamentNewsForm(request.POST)

        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.tournament_id = tournament_id
            news.save()

        return redirect("news:general_news")


class EditTournamentNewsView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id, tournament_news_id):
        if not request.user.is_authenticated:
            return redirect("users:not_logined")

        if not is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        ):
            return redirect("forbidden")

        news_for_update = TournamentNewsModel.objects.filter(
            id=tournament_news_id,
        ).first()

        form = TournamentNewsForm(instance=news_for_update)

        context = {
            "form": form,
        }

        return render(
            request,
            "news/edit_news.html",
            context=context,
        )

    def post(self, request, tournament_id, tournament_news_id):
        if not request.user.is_authenticated:
            return redirect("users:not_logined")

        if not is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        ):
            return redirect("forbidden")

        news_for_update = TournamentNewsModel.objects.filter(
            id=tournament_news_id,
        ).first()

        form = TournamentNewsForm(
            request.POST,
            instance=news_for_update,
        )

        if form.is_valid():
            form.save()

        return redirect(
            "tournaments:tournament_news",
            tournament_id=tournament_id,
        )


# Страница управления судьями турнира
class ManageJudgesView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id):
        tournament = (
            TournamentModel.objects.filter(
                id=tournament_id,
            )
            .prefetch_related("judges")
            .first()
        )

        judges = tournament.judges.all()

        context = {
            "judges": judges,
            "tournament_id": tournament_id,
            "is_owner_tournament": is_owner_tournament(
                tournament_id=tournament_id,
                user=request.user,
            ),
        }

        return render(
            request=request,
            template_name="tournaments/manage_tournament_judges.html",
            context=context,
        )


# Удаление судьи из турнира
class JudgeDeleteView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id, user_id):
        if not is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        ):
            return redirect("forbidden")

        tournament = TournamentModel.objects.filter(
            id=tournament_id,
        ).first()

        tournament.judges.remove(user_id)

        return redirect(
            "tournaments:manage_tournament_judges",
            tournament_id=tournament_id,
        )


# Добавление судьи в турнир
class AddJudgeView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id, user_id):
        if not is_owner_tournament(
            tournament_id=tournament_id,
            user=request.user,
        ):
            return redirect("forbidden")

        tournament = TournamentModel.objects.filter(
            id=tournament_id,
        ).first()

        tournament.judges.add(user_id)

        return redirect(
            "tournaments:manage_tournament_judges",
            tournament_id=tournament_id,
        )


class ManageTeamsTournamentView(LoginRequiredMixin, views.View):
    def get(self, request, tournament_id):
        teams = (
            TournamentModel.objects.filter(
                id=tournament_id,
            )
            .first()
            .team_members.all()
        )
        
        print(teams, "| teams")

        context = {
            "teams": teams,
            "tournament_id": tournament_id,
            "is_owner_tournament": is_owner_tournament(
                tournament_id=tournament_id,
                user=request.user,
            ),
        }

        return render(
            request=request,
            template_name="tournaments/manage_tournament_teams.html",
            context=context,
        )
