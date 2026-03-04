from django import views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from users.models import UserModel

from teams.forms import (
    ChangeRoleMemberTeamForm,
    InviteToTeamByEmailForm,
    TeamForm,
)
from teams.models import (
    InvitationToTeamModel,
    MemberModel,
    TeamModel,
)
from teams.utils import is_leader_for_team


class CreateTeamView(LoginRequiredMixin, views.View):
    def get(self, request):
        form = TeamForm()
        context = {
            "form": form,
        }
        return render(
            request,
            "teams/create_team.html",
            context=context,
        )

    def post(self, request):
        form = TeamForm(request.POST)

        if form.is_valid():
            created_team = form.save(commit=False)

            created_team.leader = request.user

            created_team.save()

            membership = MemberModel()

            membership.user = request.user
            membership.team = created_team
            membership.role = "Лидер"

            membership.save()

            return redirect("teams:created_teams_by_user")

        return redirect("homepage")


class TeamsCreatedByUserView(LoginRequiredMixin, views.View):
    def get(self, request):
        created_teams_by_user = TeamModel.objects.filter(
            leader=request.user,
        )

        context = {
            "created_teams_by_user": created_teams_by_user,
        }

        return render(
            request,
            "teams/created_teams_list.html",
            context=context,
        )


# Управление и просмотр списка участников
class ManageTeamView(LoginRequiredMixin, views.View):
    def get(self, request, team_id):
        if not is_leader_for_team(user_id=request.user.id, team_id=team_id):
            return redirect("forbidden")
        team = TeamModel.objects.filter(
            id=team_id,
        ).first()
        members = MemberModel.objects.filter(
            team=team_id,
        ).select_related("user")

        form_change_role_team = ChangeRoleMemberTeamForm()

        context = {
            "team": team,
            "members": members,
            "form_change_role_team": form_change_role_team,
        }

        return render(
            request,
            "teams/manage_team.html",
            context=context,
        )


class ManageInvitations(LoginRequiredMixin, views.View):
    def get(self, request, team_id):
        if not is_leader_for_team(user_id=request.user.id, team_id=team_id):
            return redirect("forbidden")

        form_invite_email = InviteToTeamByEmailForm()

        invitations = InvitationToTeamModel.objects.filter(
            team=team_id,
        ).order_by("created_at")

        context = {
            "invitations": invitations,
            "form_invite_email": form_invite_email,
        }
        return render(
            request=request,
            context=context,
            template_name="teams/manage_invitations.html",
        )

    def post(self, request, team_id):
        if not is_leader_for_team(user_id=request.user.id, team_id=team_id):
            return redirect("forbidden")

        form_invite_email = InviteToTeamByEmailForm(request.POST)

        if form_invite_email.is_valid():
            email = form_invite_email.cleaned_data["email"]
            invited_user = UserModel.objects.filter(email=email).first()
            repeat_invitation = InvitationToTeamModel.objects.filter(
                invited_user=invited_user,
                team=team_id,
            ).first()
            membership = MemberModel.objects.filter(
                user=invited_user,
                team=team_id,
            ).first()

            if invited_user is None:
                form_invite_email.add_error(
                    "email",
                    "Пользователь не найден",
                )
            elif membership is not None:
                form_invite_email.add_error(
                    "email",
                    "Пользователь уже состоит в команде",
                )
            elif (repeat_invitation is not None) and (
                repeat_invitation.status == "pending"
            ):
                form_invite_email.add_error(
                    "email",
                    "Приглашение уже было отправлено этому пользователю,\
                        он ещё не ответил",
                )
            else:
                InvitationToTeamModel.objects.create(
                    invited_user=invited_user,
                    team_id=team_id,
                )

        invitations = (
            InvitationToTeamModel.objects.select_related(
                "invited_user",
            )
            .filter(
                team=team_id,
            )
            .all()
        )

        context = {
            "invitations": invitations,
            "form_invite_email": form_invite_email,
        }

        return render(
            request=request,
            context=context,
            template_name="teams/manage_invitations.html",
        )


# Поменять роль для участника команды
class ChangeRoleTeamView(LoginRequiredMixin, views.View):
    def post(self, request, team_id, member_id):
        if not is_leader_for_team(user_id=request.user.id, team_id=team_id):
            return redirect("forbidden")

        member = MemberModel.objects.filter(
            id=member_id,
        ).first()

        form = ChangeRoleMemberTeamForm(request.POST)

        if form.is_valid():
            member.role = form.cleaned_data["role"]
            member.save()

        return redirect("teams:manage_team", team_id=team_id)


# Выгнать из команды участника
class KickMemberTeamView(LoginRequiredMixin, views.View):
    def get(self, request, team_id, member_id):
        if not is_leader_for_team(user_id=request.user.id, team_id=team_id):
            return redirect("forbidden")
        member = MemberModel.objects.filter(
            id=member_id,
        ).first()

        if is_leader_for_team(user_id=member.user.id, team_id=team_id):
            return redirect("forbidden")

        member.delete()

        return redirect("teams:manage_team", team_id=team_id)


# Принять приглашение в команду от лидера
class AcceptInvitationTeamView(LoginRequiredMixin, views.View):
    def get(self, request, invitation_id):
        invitation = InvitationToTeamModel.objects.filter(
            id=invitation_id,
        ).first()

        if request.user.id != invitation.invited_user.id:
            return redirect("forbidden")

        if invitation.status == "pending":
            invitation.status = "accepted"
            invitation.save()

            MemberModel.objects.create(
                user=invitation.invited_user,
                team=invitation.team,
                role="Участник",
            )

        return redirect("teams:show_team", team_id=invitation.team.id)


# Отклонить приглашение лидера в команду
class RejectInvitationTeamView(LoginRequiredMixin, views.View):
    def get(self, request, invitation_id):
        invitation = InvitationToTeamModel.objects.filter(
            id=invitation_id,
        ).first()

        if request.user.id != invitation.invited_user.id:
            return redirect("forbidden")

        if invitation.status == "pending":
            invitation.status = "rejected"
            invitation.save()

        return redirect("teams:show_team", team_id=invitation.team.id)


# Просмотр участников команды
class MemberTeamsView(LoginRequiredMixin, views.View):
    def get(self, request):
        memberships_by_user = (
            MemberModel.objects.filter(
                user=request.user,
            )
            .select_related("team")
            .select_related("team__leader")
            .all()
        )

        member_teams = []
        for membership in memberships_by_user:
            if membership.team.leader.id != request.user.id:
                member_teams.append(membership.team)

        return render(
            request=request,
            context={
                "member_teams": member_teams,
            },
            template_name="teams/member_teams.html",
        )


# Мои приглашения в команды
class MyInvitationsView(LoginRequiredMixin, views.View):
    def get(self, request):
        invitations_by_user = InvitationToTeamModel.objects.filter(
            invited_user=request.user,
        ).order_by("created_at")
        return render(
            request=request,
            template_name="teams/my_invitations.html",
            context={
                "invitations": invitations_by_user,
            },
        )


# Просмотр команды, если это лидер команды то пересылает на упраление
class ShowTeamView(LoginRequiredMixin, views.View):
    def get(self, request, team_id):
        if is_leader_for_team(user_id=request.user.id, team_id=team_id):
            return redirect("teams:manage_team", team_id=team_id)

        team = TeamModel.objects.filter(id=team_id).first()
        members = MemberModel.objects.filter(team=team_id).all()

        return render(
            request=request,
            template_name="teams/show_team.html",
            context={
                "team": team,
                "members": members,
            },
        )
