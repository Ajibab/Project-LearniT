import uuid
from django.db import models
from django.utils.crypto import get_random_string
from datetime import datetime, timezone
from core.models import AuditableModel
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .enums import (
    TOKEN_TYPE,
)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=40, null=True, blank=True)
    surname = models.CharField(max_length=40, null=True, blank=True)
    occupation = models.CharField(max_length=40, blank=True, null=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    phone_number = models.CharField(max_length=25, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=255, null=True)
    interests = models.TextField(max_length=40, blank=True, null=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class PendingUser(AuditableModel):
    email = models.EmailField()
    verification_code = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, null=True)

    def is_valid(self) -> bool:
        """30 mins OTP"""
        lifespan_in_seconds = float(30 * 60)

        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField()
    digital_resume = models.FileField()


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, null=True)
    token_type = models.CharField(max_length=100, choices=TOKEN_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.user)} {self.token}"

    def is_valid(self) -> bool:
        lifespan_in_seconds = float(10 * 60 * 60)
        now = datetime.now(timezone.utc)
        time_diff = now - self.created_at
        time_diff = time_diff.total_seconds()
        if time_diff >= lifespan_in_seconds:
            return False
        return True

    def verify_user(self) -> None:
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])

    def generate(self) -> None:
        if not self.token:
            self.token = get_random_string(8)
            self.save()

    def reset_user_password(self, password: str) -> None:
        self.user.set_password(password)
        self.user.save()
