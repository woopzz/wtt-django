from django.db import transaction
from django.core.exceptions import ValidationError

from rest_framework import permissions, authentication, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from .models import WorkSession
from .serializers import WorkSessionSerializer


class WorkSessionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = WorkSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def get_queryset(self):
        user = self.request.user
        queryset = WorkSession.objects.filter(owner=user)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(note__trigram_word_similar=search)

        return queryset

    def create(self, request):
        serializer = WorkSessionSerializer(data={})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=HTTP_201_CREATED)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        ws = self.get_object()

        data = JSONParser().parse(request)
        data = {'note': data.get('note')} if isinstance(data, dict) else {}

        serializer = WorkSessionSerializer(ws, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

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
