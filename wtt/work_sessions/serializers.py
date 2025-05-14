from rest_framework import serializers

from .models import WorkSession


class WorkSessionSerializer(serializers.ModelSerializer):
    note = serializers.CharField(allow_blank=True, required=False, max_length=1000)

    class Meta:
        model = WorkSession
        fields = ['id', 'started_at', 'ended_at', 'duration', 'note']
