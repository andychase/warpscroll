import uuid
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.db import models


def _days_left(start_date):
    positive = start_date - date.today() > timedelta()
    if positive:
        relative_date = relativedelta(start_date, date.today())
        years, months, days = relative_date.years, relative_date.months, relative_date.days
        for caption, item in (("year", years), ("month", months), ("day", days)):
            if item:
                yield "{} {}".format(item, caption)
                if item > 1:
                    yield "s"
                yield " "


class Trip(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    destination = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    comment = models.TextField(blank=True)
    view_only_token = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.destination

    @property
    def days_left(self):
        return "".join(_days_left(self.start_date))
