"""Provides a custom user and manager model for the user."""

from typing import (
    Any,
    ClassVar,
)

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Extends the standard user manager with basic functionality."""

    def create_user(
        self,
        username: str,
        email: str,
        password: str | None = None,
        **other_fields: Any,
    ) -> CustomUser:
        """Creates and saves a User as default user."""
        user = self.model(
            username=username,
            email=email,
            password=make_password(password),
            **other_fields,
        )
        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        username: str,
        email: str,
        password: str | None = None,
        **other_fields: Any,
    ) -> CustomUser:
        """Creates and saves a User as superuser."""
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        return self.create_user(
            username=username,
            email=email,
            password=password,
            **other_fields,
        )

    @classmethod
    def normalize_email(cls, email: str | None) -> str:
        """Converts an email address to lowercase."""
        email = super().normalize_email(email)
        return email.lower()


class CustomUser(
    AbstractBaseUser,
    PermissionsMixin,
):  # ty: ignore[invalid-attribute-override]
    """Extends the standard user model with custom manager and fields."""

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS: ClassVar[list[str]] = ['email']

    username_validator = UnicodeUsernameValidator()

    objects = CustomUserManager()

    username = models.CharField(
        _('username'),
        unique=True,
        max_length=150,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        ),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_(
            'Required. Valid email address.',
        ),
        error_messages={
            'unique': _('A user with that email already exists.'),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.',
        ),
    )
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    def clean(self) -> None:
        """Adds email normalization to the default action."""
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @classmethod
    def normalize_username(cls, username: str) -> str:
        """Converts a username to lowercase."""
        # noinspection bad-argument-type
        username = super().normalize_username(username)
        return username.lower()
