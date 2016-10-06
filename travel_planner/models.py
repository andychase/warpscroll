from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Trip(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    destination = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    comment = models.TextField()

    def __str__(self):
        return self.destination
