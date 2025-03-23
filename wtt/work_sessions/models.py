import uuid

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class WorkSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    note = models.TextField(default='')

    class Meta:
        db_table = 'wtt_work_session'

    def end(self, note=None):
        if self.ended_at:
            raise ValidationError(f'The session {self.pk} has been already ended.')

        self.ended_at = timezone.now()

        if note:
            self.note = note

        self.save()
