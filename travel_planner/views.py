from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.template.loader_tags import register

from travel_planner.models import Trip


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


def days_left(start_date):
    return "".join(_days_left(start_date))


register.filter('days_left', days_left)


def home(request):
    return render(
        request,
        "homepage.html",
        {
            "current_trips": Trip.objects.filter(
                owner=request.user,
                start_date__lte=date.today(),
                end_date__gte=date.today(),
            ),
            "upcoming_trips": Trip.objects.filter(
                owner=request.user,
                start_date__gt=date.today()
            ),
            "past_trips": Trip.objects.filter(
                owner=request.user,
                end_date__lt=date.today(),
            ).order_by("-start_date"),
            "current_day": date.today()
        }
    )
