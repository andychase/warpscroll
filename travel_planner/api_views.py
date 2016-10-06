from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

from travel_planner.models import Trip


class TripSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trip
        fields = ('destination', 'start_date', 'end_date', 'comment')


class UserTripsViewSet(viewsets.ModelViewSet):
    """ Returns a list of the current logged in user's upcoming trips ordered by start_date.
    """
    serializer_class = TripSerializer

    def get_queryset(self):
        return Trip.objects.filter(owner=self.request.user)


router = routers.DefaultRouter()
router.register(r'user_trips', UserTripsViewSet, "trip")
