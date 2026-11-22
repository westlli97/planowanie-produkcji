from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class WorkerType(models.TextChoices):
        OFFICE = "OFFICE", "Biuro"
        PRODUCTION = "PRODUCTION", "Produkcja"

    worker_type = models.CharField(
        "typ pracownika",
        max_length=12,
        choices=WorkerType.choices,
    )

    def __str__(self):
        return self.get_full_name() or self.username
