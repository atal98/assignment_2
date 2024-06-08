from django.db import models

class TaskResult(models.Model):
    job_id = models.CharField(max_length=100, unique=True)
    result = models.JSONField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_id
