from django.db import models


class VideoLink(models.Model):
    order = models.PositiveSmallIntegerField(
        verbose_name="Order Number",
        unique=True
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Step name"
    )
    message_text = models.TextField(
        verbose_name="Text message"
    )
    url = models.URLField(
        verbose_name="Video Link",
        max_length=500
    )
    delay_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Задержка отправки (в минутах)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Video Plural"
        ordering = ['order']

    def __str__(self) -> str:
        status = "🟢" if self.is_active else "🔴"
        return f"{status} step {self.order}: {self.title}"


class BotSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Bot Setting"
        verbose_name_plural = "Bot Settings"

    def __str__(self):
        return f"{self.key} = {self.value}"


class User(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, blank=True)
    tg_id = models.BigIntegerField(null=True, blank=True)
    vk_id = models.BigIntegerField(null=True, blank=True)
    is_admin = models.BooleanField(default=False, verbose_name='Admin')
    created_at = models.DateTimeField(auto_now_add=True)
    current_step = models.ForeignKey(
        VideoLink,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Current step",
        related_name="users_on_step"
    )

    class Meta:
        verbose_name = "=User="
        verbose_name_plural = "User Plural"
        indexes = [
            models.Index(fields=['tg_id']),
            models.Index(fields=['vk_id']),
        ]

    def __str__(self) -> str:
        platform = "TG" if self.tg_id else "VK" if self.vk_id else "Unknown"
        user_id = self.tg_id or self.vk_id
        return f"Пользователь {platform} | ID: {user_id}"
