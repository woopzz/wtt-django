from django.urls import path

from .views import work_session_list, work_session, work_session_end

urlpatterns = [
    path('', work_session_list),
    path('<uuid:pk>/', work_session),
    path('<uuid:pk>/end/', work_session_end),
]
