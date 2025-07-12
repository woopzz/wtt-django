from django import forms
from django.core.exceptions import ValidationError

from .models import WorkSession


class WorkSessionAdminForm(forms.ModelForm):
    class Meta:
        model = WorkSession
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        labels = cleaned_data.get('labels', [])
        owner = cleaned_data.get('owner')

        if not owner:
            ws = self.instance
            owner = ws.owner

        if labels:
            for label in labels:
                if label.owner != owner:
                    raise ValidationError(f'Label "{label}" does not belong to owner "{owner}".')

        return cleaned_data
