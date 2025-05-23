import json

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)

from ..models import WorkSession, WorkSessionLabel
from ..serializers import WorkSessionSerializer, WorkSessionLabelSerializer


class TestAPI(APITestCase):

    def setUp(self):
        super().setUp()

        self._user = self._create_user(username='main test user')

        token = Token.objects.create(user=self._user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def _create_user(self, username='test'):
        return get_user_model().objects.create_user(username)

    def _create_work_session(self, **kwargs):
        if 'owner' not in kwargs:
            kwargs['owner'] = self._user

        return WorkSession.objects.create(**kwargs)

    def _create_work_session_label(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'test'

        if 'owner' not in kwargs:
            kwargs['owner'] = self._user

        return WorkSessionLabel.objects.create(**kwargs)


class TestWorkSession(TestAPI):

    def test_create(self):
        url = reverse('work-session-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        resp_data = json.loads(response.content)
        ws = WorkSession.objects.get(pk=resp_data['id'])
        self.assertEqual(WorkSessionSerializer(ws).data, resp_data)

    # Test this constraint on the API level because we don't have the request object in the context
    # when we test serializers (and I don't want to create a fake one, at least now).
    def test_forbid_to_create_with_other_user_label(self):
        another_user = self._create_user(username='another test user')
        another_user_wsl = self._create_work_session_label(owner=another_user)

        url = reverse('work-session-list')
        response = self.client.post(url, data={'labels': [another_user_wsl.id]})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json.loads(response.content),
            {'labels': [f'Invalid pk "{another_user_wsl.id}" - object does not exist.']},
        )

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

    def test_search(self):
        ws = self._create_work_session()
        ws.end()

        ws.note = 'Gumby rides on the path of Middlesbrough'
        ws.save()

        url = reverse('work-session-list')
        response = self.client.get(url, {'search': 'Middlesbruh'})
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(WorkSessionSerializer([ws], many=True).data, resp_data['results'])

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


class TestWorkSessionLabel(TestAPI):

    def test_create(self):
        url = reverse('work-session-label-list')
        response = self.client.post(url, data={'name': 'test create'})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        resp_data = json.loads(response.content)
        wsl = WorkSessionLabel.objects.get(pk=resp_data['id'])
        self.assertEqual(WorkSessionLabelSerializer(wsl).data, resp_data)

    def test_get_list(self):
        wsl1 = self._create_work_session_label(name='first')
        wsl2 = self._create_work_session_label(name='second')

        url = reverse('work-session-label-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(WorkSessionLabelSerializer([wsl1, wsl2], many=True).data, resp_data['results'])

    def test_get_only_owned_records(self):
        my_wsl = self._create_work_session_label()

        stub_user = get_user_model().objects.get(username='stub')
        self._create_work_session_label(owner=stub_user)

        url = reverse('work-session-label-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(resp_data['count'], 1)
        self.assertEqual(WorkSessionLabelSerializer([my_wsl], many=True).data, resp_data['results'])

    def test_search(self):
        wsl = self._create_work_session_label(name='job')

        url = reverse('work-session-label-list')
        response = self.client.get(url, {'search': 'jo'})
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(WorkSessionLabelSerializer([wsl], many=True).data, resp_data['results'])

    def test_get(self):
        wsl = self._create_work_session_label()

        url = reverse('work-session-label', args=[wsl.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(WorkSessionLabelSerializer(wsl).data, resp_data)

    def test_update_name(self):
        wsl = self._create_work_session_label(name='v1')
        new_name = 'v2'

        url = reverse('work-session-label', args=[wsl.id])
        response = self.client.patch(url, data={'name': new_name})
        self.assertEqual(response.status_code, HTTP_200_OK)

        resp_data = json.loads(response.content)
        self.assertEqual(resp_data['name'], new_name)

    def test_delete(self):
        wsl = self._create_work_session_label()

        url = reverse('work-session-label', args=[wsl.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, HTTP_204_NO_CONTENT)
