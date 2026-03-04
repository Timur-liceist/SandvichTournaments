from core.models import AbstractNews
from django.db import models
from django.forms import ValidationError
from mdeditor.fields import MDTextField
from teams.models import TeamModel
from users.models import UserModel


class EventForTimeTable(models.Model):
    name = models.CharField(
        verbose_name="название",
        max_length=255,
    )
    description = MDTextField(
        verbose_name="описание",
        default="",
    )
    start_datetime = models.DateTimeField(
        verbose_name="дата и время начала",
    )
    end_datetime = models.DateTimeField(
        verbose_name="дата и время окончания",
    )
    tournament = models.ForeignKey(
        "TournamentModel",
        verbose_name="турнир",
        on_delete=models.CASCADE,
        related_name="tournament_by_timetable_events",
    )

    class Meta:
        verbose_name = "событие для расписания турнира"
        verbose_name_plural = "события для расписания турнира"

    def __str__(self):
        return f"'{self.name}'"


class TournamentModel(models.Model):
    title = models.CharField(
        verbose_name="название турнира",
        max_length=255,
    )
    owner = models.ForeignKey(
        UserModel,
        verbose_name="владелец",
        related_name="tournaments_by_owner",
        on_delete=models.SET_NULL,
        null=True,
    )
    description = MDTextField(
        verbose_name="описание",
        default="",
    )
    rules = MDTextField(
        verbose_name="правила",
        default="",
    )
    created_at = models.DateTimeField(
        verbose_name="дата и время создания",
        auto_now_add=True,
    )
    is_closed_for_requests = models.BooleanField(
        verbose_name="Закрыт ли для подачи заявок",
        default=False,
    )
    team_members = models.ManyToManyField(
        "teams.TeamModel",
        verbose_name="команды участники",
        related_name="tournaments",
        blank=True,
    )
    judges = models.ManyToManyField(
        "users.UserModel",
        verbose_name="судьи",
        related_name="tournaments_where_judge",
        blank=True,
    )

    class Meta:
        verbose_name = "турнир"
        verbose_name_plural = "турниры"

    def __str__(self):
        if self.owner:
            return f"'{self.title}' by '{self.owner.username}'"
        return f"'{self.title}' by 'DeletedUser'"


class TournamentNewsModel(AbstractNews):
    tournament = models.ForeignKey(
        TournamentModel,
        verbose_name="турнир",
        on_delete=models.CASCADE,
        related_name="news_by_tournament",
    )
    author = models.ForeignKey(
        UserModel,
        verbose_name="автор",
        on_delete=models.SET_NULL,
        null=True,
        related_name="tournament_news_by_author",
    )

    class Meta:
        verbose_name = "новость турнира"
        verbose_name_plural = "новости турниров"

    def __str__(self):
        return f"{self.title} ({self.tournament.title})"


class RequestTeamForTournamentModel(models.Model):
    CHOICES_STATUS = [
        ("pending", "Ожидается"),
        ("accepted", "Принята"),
        ("rejected", "Отклонена"),
    ]
    team = models.ForeignKey(
        TeamModel,
        on_delete=models.CASCADE,
        verbose_name="команда",
    )
    tournament = models.ForeignKey(
        TournamentModel,
        on_delete=models.CASCADE,
        verbose_name="турнир",
    )
    created_at = models.DateTimeField(
        verbose_name="дата и время отправки",
        auto_now_add=True,
    )
    status = models.CharField(
        verbose_name="статус",
        max_length=32,
        choices=CHOICES_STATUS,
        default="pending",
    )

    class Meta:
        verbose_name = "заявка команды на участие в турнире"
        verbose_name_plural = "заявки команды на участие в турнире"

    def __str__(self):
        return f"Request {self.team.name} ({self.tournament.title})"

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.status not in [choice[0] for choice in self.CHOICES_STATUS]:
            error_message = f"Недопустимое значение статуса: {self.status}"
            raise ValidationError(
                error_message,
            )


class BattleModel(models.Model):
    CHOICES_STATUS = [
        ("win_first", "Победа первой команды"),
        ("win_second", "Победа второй команды"),
        ("draw", "Ничья"),
        ("soon", "Ещё не был проведён"),
        ("problem", "Не состоялса по техническим причинам"),
    ]
    first_team = models.ForeignKey(
        TeamModel,
        verbose_name="первая команда",
        on_delete=models.SET_NULL,
        null=True,
        related_name="battles_team_first",
    )
    second_team = models.ForeignKey(
        TeamModel,
        verbose_name="вторая команда",
        on_delete=models.SET_NULL,
        null=True,
        related_name="battles_team_second",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата и время создания",
    )
    status = models.CharField(
        choices=CHOICES_STATUS,
        verbose_name="статус проведения",
        blank=False,
        default="soon",
        max_length=64,
    )
    judge = models.ForeignKey(
        "users.UserModel",
        verbose_name="судья отвечающий",
        related_name="battles_by_judge",
        on_delete=models.SET_NULL,
        null=True,
    )
    start_datetime = models.DateTimeField(
        verbose_name="дата и время начала",
    )
    proof = models.TextField(
        verbose_name="доказательство",
        default="",
    )
    tournament = models.ForeignKey(
        to=TournamentModel,
        verbose_name="турнир в котором будет проведено сражение",
        related_name="battles_by_tournament",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "сражение"
        verbose_name_plural = "сражения"

    def __str__(self):
        return f"{self.tournament} {self.created_at} {self.status}"
