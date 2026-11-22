from django.conf import settings
from django.db import models


class Notification(models.Model):
    event_type = models.CharField("typ zdarzenia", max_length=50)
    title = models.CharField("tytuł", max_length=180)
    body = models.TextField("treść", blank=True)
    url = models.CharField("adres docelowy", max_length=300, blank=True)
    created_at = models.DateTimeField("utworzono", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "powiadomienie"
        verbose_name_plural = "powiadomienia"

    def __str__(self):
        return self.title


class NotificationRecipient(models.Model):
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="recipients"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    is_read = models.BooleanField("przeczytane", default=False)
    read_at = models.DateTimeField("przeczytano", null=True, blank=True)

    class Meta:
        ordering = ["-notification__created_at", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["notification", "user"], name="unique_notification_recipient"
            )
        ]
        verbose_name = "odbiorca powiadomienia"
        verbose_name_plural = "odbiorcy powiadomień"
