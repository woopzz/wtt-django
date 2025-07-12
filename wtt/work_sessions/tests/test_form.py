from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import WorkSession, WorkSessionLabel
from ..forms import WorkSessionAdminForm


class TestWorkSessionAdminForm(TestCase):

    def _create_user(self, username='test'):
        return get_user_model().objects.create_user(username)

    def _create_work_session(self, **kwargs):
        return WorkSession.objects.create(**kwargs)

    def _create_work_session_label(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'test'

        return WorkSessionLabel.objects.create(**kwargs)

    def setUp(self):
        super().setUp()
        self._user = self._create_user()

    def test_create(self):
        wsl = self._create_work_session_label(owner=self._user)
        form = WorkSessionAdminForm(data={'owner': self._user, 'labels': [wsl.pk]})
        self.assertTrue(form.is_valid())

    def test_forbid_to_create_with_other_user_label(self):
        another_user = self._create_user(username='another test user')
        another_user_wsl = self._create_work_session_label(owner=another_user)

        form = WorkSessionAdminForm(data={'owner': self._user, 'labels': [another_user_wsl.pk]})
        self.assertFalse(form.is_valid())
        self.assertIn('does not belong to owner', str(form.errors))

    def test_forbid_to_update_with_other_user_label(self):
        another_user = self._create_user(username='another test user')
        another_user_wsl = self._create_work_session_label(owner=another_user)

        ws = WorkSession.objects.create(owner=self._user)

        form = WorkSessionAdminForm(instance=ws, data={'labels': [another_user_wsl.pk]})
        self.assertFalse(form.is_valid())
        self.assertIn('does not belong to owner', str(form.errors))
