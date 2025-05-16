from django.db import transaction
from django.core.exceptions import ValidationError

from rest_framework import permissions, authentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.status import (
    HTTP_201_CREATED, HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND,
)

from .models import WorkSession
from .serializers import WorkSessionSerializer

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([authentication.TokenAuthentication])
def work_session_list(request):
    if request.method == 'GET':
        ws = WorkSession.objects.all()
        serializer = WorkSessionSerializer(ws, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = WorkSessionSerializer(data={})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([authentication.TokenAuthentication])
def work_session(request, pk):
    try:
        ws = WorkSession.objects.get(pk=pk)
    except WorkSession.DoesNotExist:
        return Response(status=HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = WorkSessionSerializer(ws)
        return Response(serializer.data)

    if request.method == 'PATCH':
        data = JSONParser().parse(request)
        data = {'note': data.get('note')} if isinstance(data, dict) else {}

        serializer = WorkSessionSerializer(ws, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        ws.delete()
        return Response(status=HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([authentication.TokenAuthentication])
def work_session_end(request, pk):
    try:
        ws = WorkSession.objects.get(pk=pk)
    except WorkSession.DoesNotExist:
        return Response(status=HTTP_404_NOT_FOUND)

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
