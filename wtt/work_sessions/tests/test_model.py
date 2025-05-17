import uuid
import datetime as dt

from django.db import IntegrityError
from django.utils import timezone
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from freezegun import freeze_time

from ..models import WorkSession, WorkSessionLabel


class TestStart(TestCase):

    def test_should_create_record(self):
        now = timezone.now()

        with freeze_time(now):
            ws = WorkSession.objects.create()
            self.assertIsInstance(ws.id, uuid.UUID, 'Should be UUID.')
            self.assertEqual(ws.started_at, now, 'Should be set automatically.')
            self.assertIsNone(ws.ended_at, 'Should be empty initially.')
            self.assertEqual(ws.note, '', 'Should be empty initially.')
            self.assertEqual(ws.owner.username, 'stub', 'Default user.')


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


class TestWorkSessionLabel(TestCase):

    def setUp(self):
        self._user = get_user_model().objects.create_user('test')

    def test_create(self):
        name = 'first'
        wsl = WorkSessionLabel.objects.create(name=name, owner=self._user)
        self.assertIsInstance(wsl.id, uuid.UUID)
        self.assertEqual(wsl.name, name)
        self.assertEqual(wsl.owner, self._user)
        self.assertEqual(wsl.work_sessions.count(), 0)

    def test_ensure_name_is_unique_per_user(self):
        name = 'second'

        # My first label with this name.
        WorkSessionLabel.objects.create(name=name, owner=self._user)

        # Another label with this name, but it's not mine, so it's fine.
        another_user = get_user_model().objects.create_user('test2')
        WorkSessionLabel.objects.create(name=name, owner=another_user)

        # Must raise an error because I already has a label with this name.
        with self.assertRaisesRegex(IntegrityError, 'unique_name_owner'):
            WorkSessionLabel.objects.create(name=name, owner=self._user)
