from rest_framework import serializers

from .models import WorkSession


class WorkSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSession
        fields = ['id', 'started_at', 'ended_at', 'duration', 'note']
        read_only_fields = ['id', 'started_at', 'ended_at', 'duration']

    def validate(self, attrs):
        if 'note' in attrs and not (self.instance and self.instance.ended()):
            raise serializers.ValidationError('You cannot change the note if the session has not ended yet.')

        return super().validate(attrs)
