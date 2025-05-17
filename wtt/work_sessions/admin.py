from django.urls import reverse
from django.utils.html import format_html_join
from django.contrib import admin

from .models import WorkSession, WorkSessionLabel

def complete_sessions(modeladmin, request, queryset):
    for ws in queryset:
        ws.end()


class WorkSessionAdmin(admin.ModelAdmin):
    fields = ['id', 'owner', 'labels', 'started_at', 'ended_at', 'duration', 'note']
    readonly_fields = ['id', 'started_at', 'ended_at', 'duration']
    actions = [complete_sessions]

    def get_readonly_fields(self, request, obj=None):
        result = super().get_readonly_fields(request, obj=obj)

        if not (obj and obj.ended()):
            result = result + ['note']

        # Allow to specify a user on create, but forbid to change it.
        if obj:
            result = result + ['owner']

        return result

admin.site.register(WorkSession, WorkSessionAdmin)


class WorkSessionLabelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner']

    fields = ['id', 'name', 'owner', 'related_work_sessions']
    readonly_fields = ['id', 'related_work_sessions']

    def related_work_sessions(self, obj):
        if not obj.pk:
            return ''

        return format_html_join(
            '',
            '<div><a href="{}">{}</a></div>',
            ((
                reverse('admin:work_sessions_worksession_change', args=(ws.id,)),
                ws,
            ) for ws in obj.work_sessions.all()),
        )

    related_work_sessions.short_description = 'Work Sessions'

    def get_readonly_fields(self, request, obj=None):
        result = super().get_readonly_fields(request, obj=obj)

        if obj:
            result = result + ['owner']

        return result

admin.site.register(WorkSessionLabel, WorkSessionLabelAdmin)
