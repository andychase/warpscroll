from datetime import datetime

from django.shortcuts import render

from travel_planner.models import Trip


def get_upcoming_trips(user):
    for trip in Trip.objects.filter(owner=user, start_date__gt=datetime.now()).order_by("-start_date"):
        # trip.days_left = datetime.now() - trip.start_date
        yield trip


def home(request):
    return render(
        request,
        "base.html",
        {
            "current_trips": Trip.objects.filter(
                owner=request.user,
                start_date__lt=datetime.now(),
                end_date__gt=datetime.now(),
            ),
            "upcoming_trips": list(get_upcoming_trips(request.user)),
            "past_trips": Trip.objects.filter(
                owner=request.user,
                end_date__lt=datetime.now(),
            ).order_by("-start_date"),
            "current_day": datetime.now()
        }
    )
