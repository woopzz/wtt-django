import uuid
import datetime as dt

from django.utils import timezone
from django.test import TestCase
from django.core.exceptions import ValidationError

from freezegun import freeze_time

from ..models import WorkSession


class TestStart(TestCase):

    def test_should_create_record(self):
        now = timezone.now()

        with freeze_time(now):
            ws = WorkSession.objects.create()
            self.assertIsInstance(ws.id, uuid.UUID, 'Should be UUID.')
            self.assertEqual(ws.started_at, now, 'Should be set automatically.')
            self.assertIsNone(ws.ended_at, 'Should be empty initially.')
            self.assertEqual(ws.note, '', 'Should be empty initially.')


class TestEnd(TestCase):

    def setUp(self):
        super().setUp()
        self._ws = WorkSession.objects.create()

    def test_should_close_session(self):
        duration = 45
        now = self._ws.started_at + dt.timedelta(minutes=duration)
        with freeze_time(now):
            self._ws.end()
            self.assertEqual(self._ws.ended_at, now, 'Should be now.')
            self.assertEqual(
                self._ws.duration, duration,
                'Should be a number of minutes between the end moment and the start moment.',
            )

    def test_should_close_session(self):
        self._ws.end()
        self.assertTrue(self._ws.ended())

    def test_should_forbid_to_end_an_already_ended_session(self):
        self._ws.end()

        with self.assertRaisesMessage(ValidationError, 'already ended'):
            self._ws.end()
