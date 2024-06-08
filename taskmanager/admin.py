from django.contrib import admin
from .models import TaskResult

@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ('job_id', 'date_created')
