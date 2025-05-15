from django.urls import path

from .views import work_session_list, work_session, work_session_end

urlpatterns = [
    path('', work_session_list, name='work-session-list'),
    path('<uuid:pk>/', work_session, name='work-session'),
    path('<uuid:pk>/end/', work_session_end, name='work-session-end'),
]
