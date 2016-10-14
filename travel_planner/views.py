from datetime import date, datetime

from dateutil.tz import tzoffset
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect

from travel_planner.models import Trip


def home(request):
    if request.user.is_anonymous:
        return render(
            request,
            "homepage.html"
        )
    else:
        if request.session.get("time_zone"):
            time_zone = request.session.get("time_zone") * 60 * 60
            today = datetime.now(tz=tzoffset("user", time_zone)).date()
        else:
            today = date.today()
        return render(
            request,
            "homepage.html", {
                "user": request.user,
                "current_trips": Trip.objects.filter(
                    owner=request.user,
                    start_date__lte=today,
                    end_date__gte=today
                ).order_by("start_date", "-id"),
                "upcoming_trips": Trip.objects.filter(
                    owner=request.user,
                    start_date__gt=today
                ).order_by("start_date", "-id"),
                "past_trips": Trip.objects.filter(
                    owner=request.user,
                    end_date__lt=today
                ).order_by("start_date", "-id"),
                "current_day": today
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


def ajax_login(request):
    if request.POST.get("time_zone"):
        request.session['time_zone'] = int(request.POST.get("time_zone"))
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        login(request, form.get_user())
        return JsonResponse({
            "OK": True,
            "admin": form.get_user().is_staff
        })
    else:
        return HttpResponseBadRequest("Incorrect username or password")


def ajax_change_password(request):
    old_password = request.POST.get("old_password")
    new_password = request.POST.get("new_password")
    confirm_password = request.POST.get("confirm_password")
    if not request.user.check_password(old_password):
        return HttpResponseBadRequest('Original password not correct')
    elif not new_password:
        return HttpResponseBadRequest('New password must not be blank')
    elif new_password != confirm_password:
        return HttpResponseBadRequest("New password doesn't match")
    else:
        request.user.set_password(new_password)
        request.user.save()
        login(request, request.user)
        return JsonResponse({"OK": True})
