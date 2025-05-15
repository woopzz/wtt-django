from django.contrib import admin

from .models import WorkSession

def complete_sessions(modeladmin, request, queryset):
    for ws in queryset:
        ws.end()


class WorkSessionAdmin(admin.ModelAdmin):
    fields = ['id', 'started_at', 'ended_at', 'duration', 'note']
    readonly_fields = ['id', 'started_at', 'ended_at', 'duration']
    actions = [complete_sessions]

    def get_readonly_fields(self, request, obj=None):
        result = super().get_readonly_fields(request, obj=obj)

        if not (obj and obj.ended()):
            result = result + ['note']

        return result

admin.site.register(WorkSession, WorkSessionAdmin)
