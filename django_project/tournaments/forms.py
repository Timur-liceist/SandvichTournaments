import mdeditor
from django import forms
from mdeditor.widgets import MDEditorWidget
from teams.models import TeamModel
from users.models import UserModel

from tournaments.models import (
    BattleModel,
    TournamentModel,
    TournamentNewsModel,
)


class TournamentCreateForm(forms.ModelForm):
    title = forms.CharField(
        label="Название турнира",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите название турнира",
            },
        ),
        required=True,
    )
    rules = forms.CharField(
        label="Правила турнира",
        widget=mdeditor.fields.MDEditorWidget(
            attrs={
                "class": "form-control",
                "placeholder": "Введите правила турнира",
            },
        ),
        required=False,
    )
    description = forms.CharField(
        label="Описание турнира",
        widget=mdeditor.fields.MDEditorWidget(
            attrs={
                "class": "form-control",
                "placeholder": "Введите описание турнира",
            },
        ),
        required=False,
    )
    is_closed_for_requests = forms.BooleanField(
        label="Пока нелья подать заявку на участие в турнир",
        required=False,
        widget=forms.CheckboxInput(),
    )

    class Meta:
        model = TournamentModel
        fields = [
            "title",
            "rules",
            "description",
            "is_closed_for_requests",
        ]


class RequestTeamTournamentForm(forms.Form):
    team = forms.ModelChoiceField(
        label="Выбирите команду от которой посылаете запрос на участие",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "Выбери команду",
            },
        ),
        queryset=TeamModel.objects,
        required=True,
    )

    def set_team_selecting(self, leader_user):
        self.fields["team"].queryset = TeamModel.objects.filter(
            leader=leader_user,
        )

    class Meta:
        fields = [
            "team",
        ]


class BattleForm(forms.ModelForm):
    first_team = forms.ModelChoiceField(
        label="Первая команда",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "Выбери команду",
            },
        ),
        queryset=TeamModel.objects,
    )
    second_team = forms.ModelChoiceField(
        label="Вторая команда",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "Выберите команду",
            },
        ),
        queryset=TeamModel.objects,
    )
    judge = forms.ModelChoiceField(
        label="Судья",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "placeholder": "Выберите пользователя",
            },
        ),
        queryset=UserModel.objects,
    )
    start_datetime = forms.DateTimeField(
        label="Дата и время начала сражения",
        widget=forms.widgets.DateTimeInput(
            attrs={
                "class": "form-control",
                "type": "datetime-local",
                "placeholder": "Выберите дату и время",
            },
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M"],
    )

    def set_team_selecting(
        self,
        teams_by_tournament,
        judges_by_tournament,
    ):
        self.fields["first_team"].queryset = teams_by_tournament
        self.fields["second_team"].queryset = teams_by_tournament
        self.fields["judge"].queryset = judges_by_tournament

    class Meta:
        model = BattleModel
        fields = [
            "first_team",
            "second_team",
            "judge",
            "start_datetime",
        ]


class TournamentNewsForm(forms.ModelForm):
    class Meta:
        model = TournamentNewsModel

        fields = [
            "title",
            "content",
        ]
        widgets = {
            "content": MDEditorWidget(),
        }
