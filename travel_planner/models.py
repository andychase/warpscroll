from django.contrib.auth.models import User
from django.db import models
import uuid


class Trip(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    destination = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    comment = models.TextField(blank=True)
    view_only_token = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.destination
