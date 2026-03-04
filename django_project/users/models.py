from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManagerForEmail(BaseUserManager):
    def create_user(
        self, email, steamid64=None, password=None, **extra_fields,
    ):
        if not email:
            raise ValueError("Поле Email обязательно")

        if not steamid64:
            raise ValueError("Поле SteamID64 обязательно")

        email = self.normalize_email(email)

        user = self.model(email=email, steamid64=steamid64, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email, steamid64, password=None, **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, steamid64, password, **extra_fields)


class UserModel(AbstractUser):
    last_name = None
    first_name = None
    password = None

    steamid64 = models.CharField(
        verbose_name="steamid64",
        max_length=32,
        unique=True,
    )
    bio = models.TextField(
        verbose_name="биография",
        default="",
        validators=[
            MaxLengthValidator(2048),
        ],
    )
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=32,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer.\
            Letters, digits and @/./+/-/_ only.",
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        verbose_name="почта",
        unique=True,
    )
    is_public_profile = models.BooleanField(
        verbose_name="возможность просмотра профиля другими игроками",
        default=True,
    )

    objects = UserManagerForEmail()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["steamid64"]


    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.username}"
