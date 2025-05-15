import datetime as dt

from django.test import TestCase

from ..models import WorkSession
from ..serializers import WorkSessionSerializer


class TestWorkSessionSerializer(TestCase):

    def test_create(self):
        serializer = WorkSessionSerializer(data={})
        serializer.is_valid(raise_exception=True)
        ws = serializer.save()
        self.assertIsInstance(ws, WorkSession)

    def test_read(self):
        ws = WorkSession.objects.create()
        data = WorkSessionSerializer(ws).data
        self.assertEqual(dt.datetime.fromisoformat(data['started_at']), ws.started_at)
        self.assertEqual(data['ended_at'], ws.ended_at)
        self.assertEqual(data['duration'], ws.duration)
        self.assertEqual(data['note'], ws.note)
