import datetime as dt

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.test import APIRequestFactory

from ..models import WorkSession, WorkSessionLabel
from ..serializers import WorkSessionSerializer, WorkSessionLabelSerializer, WorkSessionLabelDetailsSerializer


class TestSerializer(TestCase):

    def _create_user(self, username='test'):
        return get_user_model().objects.create_user(username)

    def _create_work_session(self, **kwargs):
        return WorkSession.objects.create(**kwargs)

    def _create_work_session_label(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'test'

        return WorkSessionLabel.objects.create(**kwargs)


class TestWorkSessionSerializer(TestSerializer):

    def setUp(self):
        super().setUp()
        self._user = self._create_user()
        self._wsl = self._create_work_session_label(owner=self._user)

    def test_create(self):
        serializer = WorkSessionSerializer(data={'labels': [self._wsl.id]})
        serializer.is_valid(raise_exception=True)

        ws = serializer.save(owner=self._user)
        self.assertIsInstance(ws, WorkSession)
        self.assertEqual(ws.owner, self._user)
        self.assertIn(self._wsl, ws.labels.all())

    def test_read(self):
        ws = WorkSession.objects.create()
        ws.labels.add(self._wsl)
        serialized_labels = WorkSessionLabelDetailsSerializer([self._wsl], many=True).data

        data = WorkSessionSerializer(ws).data
        self.assertEqual(dt.datetime.fromisoformat(data['started_at']), ws.started_at)
        self.assertEqual(data['ended_at'], ws.ended_at)
        self.assertEqual(data['duration'], ws.duration)
        self.assertEqual(data['note'], ws.note)
        self.assertEqual(data['label_details'], serialized_labels)

    def test_forbid_to_create_with_other_user_label(self):
        another_user = self._create_user(username='another test user')
        another_user_wsl = self._create_work_session_label(owner=another_user)

        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = self._user

        serializer = WorkSessionSerializer(
            data={'labels': [another_user_wsl.id]},
            context={'request': request},
        )
        is_valid = serializer.is_valid()
        self.assertFalse(is_valid)
        self.assertEqual(serializer.errors['labels'][0].code, 'does_not_exist')


class TestWorkSessionLabelSerializer(TestSerializer):

    def setUp(self):
        super().setUp()
        self._user = self._create_user()

    def test_create(self):
        serializer = WorkSessionLabelSerializer(data={'name': 'test'})
        serializer.is_valid(raise_exception=True)
        wsl = serializer.save(owner=self._user)
        self.assertIsInstance(wsl, WorkSessionLabel)
        self.assertEqual(wsl.owner, self._user)

    def test_forbid_to_create_dup(self):
        name = 'same label for same user'
        self._create_work_session_label(name=name, owner=self._user)

        serializer = WorkSessionLabelSerializer(data={'name': name})
        serializer.is_valid(raise_exception=True)
        with self.assertRaisesRegex(serializers.ValidationError, 'already have a label'):
            serializer.save(owner=self._user)

    def test_read(self):
        wsl = self._create_work_session_label(owner=self._user)

        ws = self._create_work_session(owner=self._user)
        ws.labels.set([wsl])
        serialized_work_sessions = [ws.id]

        data = WorkSessionLabelSerializer(wsl).data
        self.assertEqual(data['id'], str(wsl.id))
        self.assertEqual(data['name'], wsl.name)
        self.assertEqual(data['work_sessions'], serialized_work_sessions)


class TestWorkSessionLabelDetailsSerializer(TestSerializer):

    def test_read(self):
        name = 'test wsl details'
        owner = self._create_user()
        wsl = self._create_work_session_label(name=name, owner=owner)
        self.assertEqual(
            WorkSessionLabelDetailsSerializer(wsl).data,
            {'id': str(wsl.id), 'name': name},
        )
