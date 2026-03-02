from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Status(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("имя"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Метка")
        verbose_name_plural = _("Метки")

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.ForeignKey("Status", on_delete=models.PROTECT)
    author = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="tasks_authored"
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks_executed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    labels = models.ManyToManyField(Label, verbose_name="метки", blank=True)

    class Meta:
        verbose_name = _("Задача")
        verbose_name_plural = _("Задачи")

    def __str__(self):
        return self.name
