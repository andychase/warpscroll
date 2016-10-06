# Warp Scroll
*Plan your trip through anywhere*

Warp Scroll is a new type of travel planner which was primary designed with video game players in mind.
Although it supports traditional travel plans, its unique branding and design inspires creative use cases to
capture a niche market.

## Installation

You'll need python-3.5.2 and pip.

First install the dependancies:

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
