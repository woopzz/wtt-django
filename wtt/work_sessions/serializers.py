from rest_framework import serializers

from .models import WorkSession, WorkSessionLabel


class WorkSessionLabelDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSessionLabel
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class WorkSessionSerializer(serializers.ModelSerializer):
    labels = serializers.PrimaryKeyRelatedField(
        queryset=WorkSessionLabel.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    label_details = WorkSessionLabelDetailsSerializer(
        source='labels',
        many=True,
        read_only=True,
    )

    class Meta:
        model = WorkSession
        fields = ['id', 'started_at', 'ended_at', 'duration', 'note', 'labels', 'label_details']
        read_only_fields = ['id', 'started_at', 'ended_at', 'duration', 'label_details']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'request' in self.context:
            user = self.context['request'].user

            # Forbid to attach labels of other users.
            field_labels = self.fields['labels'].child_relation
            field_labels.queryset = field_labels.queryset.filter(owner=user)

    def validate(self, attrs):
        if 'note' in attrs and not (self.instance and self.instance.ended()):
            raise serializers.ValidationError('You cannot change the note if the session has not ended yet.')

        return super().validate(attrs)


class WorkSessionLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSessionLabel
        fields = ['id', 'name', 'work_sessions']
        read_only_fields = ['id', 'work_sessions']

    def create(self, validated_data):
        name = validated_data.get('name')
        owner = validated_data.get('owner')
        assert name, f'Name is a required field, but its value is "{name}".'
        assert owner, f'Owner is a required field, but its value is "{owner}".'
        if WorkSessionLabel.objects.filter(name=name, owner=owner).exists():
            raise serializers.ValidationError(f'You already have a label with the name "{name}".')

        return super().create(validated_data)
