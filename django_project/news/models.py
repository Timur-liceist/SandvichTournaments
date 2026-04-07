from core.models import AbstractNews
from django.db import models
from users.models import UserModel


class GeneralNewsModel(AbstractNews):
    author = models.ForeignKey(
        UserModel,
        verbose_name="автор",
        on_delete=models.SET_NULL,
        null=True,
        related_name="general_news_by_user",
    )

    class Meta:
        verbose_name = "общая новость сайта"
        verbose_name_plural = "общие новости сайта"

    def __str__(self):
        return self.title


# Лайк для генеральной новости
class LikeToGeneralNews(models.Model):
    user = models.ForeignKey(
        verbose_name="пользователь",
        to="users.UserModel",
        on_delete=models.CASCADE,
        related_name="likes_to_general_news",
    )
    general_news = models.ForeignKey(
        "tournaments.TournamentNewsModel",
        related_name="likes_to_general_news",
        verbose_name="генеральная новость",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "лайк на генеральную новость"
        verbose_name_plural = "лайки на генеральную новость"

    def __str__(self):
        return f"Like to {self.general_news} from user {self.user}"


# ДизЛайк для генеральной новости
class DislikeToGeneralNews(models.Model):
    user = models.ForeignKey(
        verbose_name="пользователь",
        to="users.UserModel",
        on_delete=models.CASCADE,
        related_name="dislikes_to_general_news",
    )
    general_news = models.ForeignKey(
        "tournaments.TournamentNewsModel",
        related_name="dislikes_by_general_news",
        verbose_name="генеральная новость",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "дизлайк на генеральную новость"
        verbose_name_plural = "дизлайки на генеральную новость"

    def __str__(self):
        return f"Dis Like to {self.general_news} from user {self.user}"
