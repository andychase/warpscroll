# Warp Scroll
*Plan your trip through anywhere*

This project was a coding test, I think I would probably use a calendar realistically.

Warp Scroll is a date-only itinerary planner. You could use it to plan your quests during your iron man speed-run through runescape.

## Installation

You'll need python-3.5.2 and pip.

First install the dependencies:

    pip3 install -r requirements.txt

Next migrate your database if needed:

    python3 manage.py migrate

Finally create a superuser if needed:

    python3 manage.py createsuperuser

## Running

To run in debug:

    python3 manage.py runserver

To run in production:

    DJANGO_SETTINGS_MODULE=warpscroll.production gunicorn warpscroll.wsgi --log-file -
