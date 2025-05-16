import json

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,
)

from ..models import WorkSession
from ..serializers import WorkSessionSerializer


class TestAPI(APITestCase):

    def setUp(self):
        super().setUp()

        self._user = get_user_model().objects.create_user('test')

        token = Token.objects.create(user=self._user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def _create_work_session(self, **kwargs):
        if 'owner' not in kwargs:
            kwargs['owner'] = self._user

        return WorkSession.objects.create(**kwargs)

    def test_create(self):
        url = reverse('work-session-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        resp_data = json.loads(response.content)
        ws = WorkSession.objects.get(pk=resp_data['id'])
        self.assertEqual(WorkSessionSerializer(ws).data, resp_data)

    def test_get_list(self):
        ws1 = self._create_work_session()
        ws2 = self._create_work_session()
        ws2.end()

        url = reverse('work-session-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(WorkSessionSerializer([ws2, ws1], many=True).data, resp_data['results'])

    def test_get_only_owned_records(self):
        my_ws = self._create_work_session()

        stub_user = get_user_model().objects.get(username='stub')
        self._create_work_session(owner=stub_user)

        url = reverse('work-session-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(resp_data['count'], 1)
        self.assertEqual(WorkSessionSerializer([my_ws], many=True).data, resp_data['results'])

    def test_get(self):
        ws = self._create_work_session()

        url = reverse('work-session', args=[ws.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(WorkSessionSerializer(ws).data, resp_data)

    def test_update_note(self):
        ws = self._create_work_session()
        ws.end()

        new_note = 'test note'

        url = reverse('work-session', args=[ws.id])
        response = self.client.patch(url, data={'note': new_note})
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(resp_data['note'], new_note)

    def test_forbid_to_change_note_if_session_has_not_ended_yet(self):
        ws = self._create_work_session()

        url = reverse('work-session', args=[ws.id])
        response = self.client.patch(url, data={'note': 'some text'})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        resp_data = json.loads(response.content)
        self.assertIn(
            'You cannot change the note if the session has not ended yet.',
            resp_data['non_field_errors'],
        )

    def test_delete(self):
        ws = self._create_work_session()

        url = reverse('work-session', args=[ws.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)

    def test_end(self):
        ws = self._create_work_session()

        url = reverse('work-session-end', args=[ws.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

        ws.refresh_from_db()
        self.assertTrue(ws.ended())

    def test_end_with_note(self):
        ws = self._create_work_session()
        new_note = 'finally x_x'

        url = reverse('work-session-end', args=[ws.id])
        response = self.client.post(url, data={'note': new_note})
        self.assertEqual(response.status_code, HTTP_200_OK)

        ws.refresh_from_db()
        self.assertTrue(ws.ended())
        self.assertEqual(ws.note, new_note)
