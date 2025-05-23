import uuid

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex

DT_FORMAT = '%d.%m.%Y %H:%M:%S'


class WorkSession(models.Model):

    def owner_default():
        return get_user_model().objects.get(username='stub').id

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(
        verbose_name='Duration, mins',
        blank=True,
        null=True,
    )
    note = models.TextField(
        blank=True,
        default='',
        max_length=1000,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='work_sessions',
        on_delete=models.CASCADE,
        default=owner_default,
    )
    labels = models.ManyToManyField(
        'work_sessions.WorkSessionLabel',
        related_name='work_sessions',
        blank=True,
    )

    class Meta:
        db_table = 'wtt_work_session'
        ordering = ['-started_at', '-ended_at']
        indexes = [
            GinIndex(name='note_trgm_gin', fields=['note'], opclasses=['gin_trgm_ops']),
        ]

    def __str__(self):
        name = self.started_at.strftime(DT_FORMAT)
        if self.ended_at:
            name += ' - ' + self.ended_at.strftime(DT_FORMAT)
        return name

    def ended(self):
        return bool(self.ended_at)

    def end(self):
        if self.ended_at:
            raise ValidationError(f'The session {self.pk} has been already ended.')

        self.ended_at = timezone.now()
        self.duration = (self.ended_at - self.started_at).total_seconds() // 60
        self.save()


class WorkSessionLabel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='work_session_labels',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'wtt_work_session_label'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'owner'], name='unique_name_owner'),
        ]
        indexes = [
            GinIndex(name='wsl_name_trgm_gin', fields=['name'], opclasses=['gin_trgm_ops']),
        ]

    def __str__(self):
        return f'{self.name} (by {self.owner})'
