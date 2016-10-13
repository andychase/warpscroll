"""warpscroll URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token

from travel_planner import api_views
from travel_planner.views import home, save_trip, add_trip, remove_trip, ajax_login, ajax_change_password

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^save-trip/$', save_trip, name='save_trip'),
    url(r'^add-trip/$', add_trip, name='add_trip'),
    url(r'^remove-trip/$', remove_trip, name='remove_trip'),
    url(r'^login/$', ajax_login, name='login'),
    url(r'^change_password/$', ajax_change_password, name='change_user_password'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(api_views.router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', obtain_auth_token),
]
