from rest_framework import permissions
from rest_framework import routers, serializers, viewsets

from travel_planner.models import Trip


class UserTripPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class TripSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trip
        fields = ('url', 'destination', 'start_date', 'end_date', 'comment')
        owner = serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            lookup_field='id',
            many=True,
            read_only=True
        )


class UserTripsViewSet(viewsets.ModelViewSet):
    """ Returns a list of the current logged in user's upcoming trips ordered by start_date.
    """
    serializer_class = TripSerializer
    permission_classes = (UserTripPermission,)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Trip.objects.none()
        else:
            return Trip.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


router = routers.DefaultRouter()
router.register(r'user_trips', UserTripsViewSet, "trip")
