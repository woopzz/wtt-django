import uuid

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

DT_FORMAT = '%d.%m.%Y %H:%M:%S'


class WorkSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(
        verbose_name='Duration, mins',
        blank=True,
        null=True,
    )
    note = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'wtt_work_session'
        ordering = ['-started_at', '-ended_at']

    def __str__(self):
        name = self.started_at.strftime(DT_FORMAT)
        if self.ended_at:
            name += ' - ' + self.ended_at.strftime(DT_FORMAT)
        return name

    def end(self, note=None):
        if self.ended_at:
            raise ValidationError(f'The session {self.pk} has been already ended.')

        self.ended_at = timezone.now()
        self.duration = (self.ended_at - self.started_at).total_seconds() // 60

        if note:
            self.note = note

        self.save()
