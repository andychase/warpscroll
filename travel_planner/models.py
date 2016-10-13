import uuid
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzoffset
from django.contrib.auth.models import User
from django.db import models


def _days_left(start_date, timezone=None):
    if not start_date:
        return
    if timezone:
        today = datetime.now(tz=tzoffset("user", timezone)).date()
    else:
        today = date.today()
    positive = start_date - today > timedelta()
    if positive:
        relative_date = relativedelta(start_date, today)
        years, months, days = relative_date.years, relative_date.months, relative_date.days
        for caption, item in (("year", years), ("month", months), ("day", days)):
            if item:
                yield "{} {}".format(item, caption)
                if item > 1:
                    yield "s"
                yield " "


class Trip(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.CharField(blank=True, max_length=200)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    comment = models.TextField(blank=True)
    view_only_token = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return self.destination

    def days_left(self, timezone=None):
        days_left_value = "".join(_days_left(self.start_date, timezone))
        if days_left_value:
            days_left_value += " until trip"
        return days_left_value
