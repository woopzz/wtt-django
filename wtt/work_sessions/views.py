import datetime as dt

from django.db import transaction
from django.core.exceptions import ValidationError

from rest_framework import permissions, authentication
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import WorkSession, WorkSessionLabel
from .serializers import WorkSessionSerializer, WorkSessionLabelSerializer


class WorkSessionViewSet(ModelViewSet):
    serializer_class = WorkSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        params = self.request.query_params
        queryset = WorkSession.objects.filter(owner=user)

        search = params.get('search')
        if search:
            queryset = queryset.filter(note__trigram_word_similar=search)

        started_at = params.get('started_at')
        if started_at:
            queryset = queryset.filter(started_at__gte=try_to_parse_datetime_string(started_at))

        ended_at = params.get('ended_at')
        if ended_at:
            queryset = queryset.filter(ended_at__lte=try_to_parse_datetime_string(ended_at))

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True)
    def end(self, request, pk):
        ws = self.get_object()

        with transaction.atomic():
            try:
                ws.end()
            except ValidationError as exc:
                return Response({'detail': str(exc)}, status=HTTP_400_BAD_REQUEST)

            data = request.data if request.body else {}
            serializer = WorkSessionSerializer(ws, data=data)
            serializer.is_valid(raise_exception=True)

            new_note = serializer.validated_data.get('note')
            if new_note:
                ws.note = new_note
                ws.save()

            return Response(serializer.data)


class WorkSessionLabelViewSet(ModelViewSet):
    serializer_class = WorkSessionLabelSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        queryset = WorkSessionLabel.objects.filter(owner=user)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__trigram_word_similar=search)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

def try_to_parse_datetime_string(value):
    try:
        return dt.datetime.fromisoformat(value).replace(tzinfo=dt.timezone.utc)
    except Exception:
        raise DRFValidationError(f'"{value}" is not a valid ISO 8601 formated datetime string.')
