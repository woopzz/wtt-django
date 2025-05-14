from rest_framework import serializers

from .models import WorkSession


class WorkSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSession
        fields = ['id', 'started_at', 'ended_at', 'duration', 'note']
