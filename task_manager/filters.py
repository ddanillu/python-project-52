import django_filters
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from .models import Task, Status, Label


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(), label=_("Статус")
    )
    executor = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(is_active=True).exclude(
            is_staff=True, is_superuser=True
        ),
        label=_("Исполнитель"),
    )
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.all(), label=_("Метка")
    )
    author = django_filters.BooleanFilter(
        method="filter_author_tasks",
        label=_("Только свои задачи"),
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = Task
        fields = ["status", "executor", "labels", "author"]

    def filter_author_tasks(self, queryset, name, value):
        return queryset.filter(author=self.request.user) if value else queryset
