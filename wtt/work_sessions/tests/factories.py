from django.contrib.auth import get_user_model

from ..models import WorkSession, WorkSessionLabel


class TestFactories():

    def _create_user(self, username='test'):
        return get_user_model().objects.create_user(username)

    def _create_work_session(self, **kwargs):
        return WorkSession.objects.create(**kwargs)

    def _create_work_session_label(self, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = 'test'

        return WorkSessionLabel.objects.create(**kwargs)
