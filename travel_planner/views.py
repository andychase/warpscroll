from datetime import date, datetime
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, redirect
from travel_planner.models import Trip


def home(request):
    if request.user.is_anonymous:
        return render(
            request,
            "homepage.html"
        )
    else:
        return render(
            request,
            "homepage.html", {
                "user": request.user,
                "current_trips": Trip.objects.filter(
                    owner=request.user,
                    start_date__lte=date.today(),
                    end_date__gte=date.today(),
                ).order_by("-start_date"),
                "upcoming_trips": Trip.objects.filter(
                    owner=request.user,
                    start_date__gt=date.today()
                ).order_by("-start_date"),
                "past_trips": Trip.objects.filter(
                    owner=request.user,
                    end_date__lt=date.today(),
                ).order_by("-start_date"),
                "current_day": date.today()
            }
        )


def convert_date(date_string):
    if date_string:
        return datetime.strptime(date_string, "%b. %d, %Y")


def save_trip(request):
    trip_id = request.POST.get("trip-id")
    trip = Trip.objects.get(id=trip_id)
    if not trip:
        return HttpResponseNotFound('<h1>Trip not found</h1>')
    if trip.owner != request.user:
        raise PermissionDenied
    if request.POST.get("delete"):
        return remove_trip(request, trip)
    trip.destination = request.POST.get("destination")
    trip.start_date = convert_date(request.POST.get("start_date"))
    if not request.POST.get("end_date"):
        trip.end_date = trip.start_date
    else:
        trip.end_date = convert_date(request.POST.get("end_date"))
    trip.comment = request.POST.get("comment")
    trip.save()
    return redirect('home')


def add_trip(request):
    if request.user.is_anonymous:
        return HttpResponseBadRequest('<h1>Must be logged in</h1>')
    trip = Trip()
    trip.owner = request.user
    trip.start_date = datetime.now()
    trip.end_date = datetime.now()
    trip.save()
    return redirect('home')


def remove_trip(request, trip):
    trip.delete()
    return redirect('home')
