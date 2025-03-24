from django.contrib import admin

from .models import WorkSession

def complete_sessions(modeladmin, request, queryset):
    for ws in queryset:
        ws.end()


class WorkSessionAdmin(admin.ModelAdmin):
    fields = ['id', 'started_at', 'ended_at', 'note']
    readonly_fields = ['id', 'started_at', 'ended_at']
    actions = [complete_sessions]

    def get_readonly_fields(self, request, obj=None):
        result = super().get_readonly_fields(request, obj=obj)

        completed = obj and obj.ended_at
        if not completed:
            result = result + ['note']

        return result

admin.site.register(WorkSession, WorkSessionAdmin)
