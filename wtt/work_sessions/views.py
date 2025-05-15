from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError

from rest_framework import permissions, authentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.parsers import JSONParser

from .models import WorkSession
from .serializers import WorkSessionSerializer

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([authentication.TokenAuthentication])
def work_session_list(request):
    if request.method == 'GET':
        ws = WorkSession.objects.all()
        serializer = WorkSessionSerializer(ws, many=True)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'POST':
        serializer = WorkSessionSerializer(data={})
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)

        return JsonResponse(serializer.errors, status=400)

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([authentication.TokenAuthentication])
def work_session(request, pk):
    try:
        ws = WorkSession.objects.get(pk=pk)
    except WorkSession.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = WorkSessionSerializer(ws)
        return JsonResponse(serializer.data)

    if request.method == 'PATCH':
        data = JSONParser().parse(request)
        data = {'note': data.get('note')} if isinstance(data, dict) else {}

        serializer = WorkSessionSerializer(ws, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)

        return JsonResponse(serializer.errors, status=400)

    if request.method == 'DELETE':
        ws.delete()
        return HttpResponse(status=204)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([authentication.TokenAuthentication])
def work_session_end(request, pk):
    try:
        ws = WorkSession.objects.get(pk=pk)
    except WorkSession.DoesNotExist:
        return HttpResponse(status=404)

    try:
        ws.end()
    except ValidationError as exc:
        return JsonResponse({'detail': str(exc)}, status=400)

    data = JSONParser().parse(request) if request.body else {}
    serializer = WorkSessionSerializer(ws, data=data)
    serializer.is_valid(raise_exception=True)

    new_note = serializer.validated_data.get('note')
    if new_note:
        ws.note = new_note
        ws.save()

    return JsonResponse(serializer.data)
