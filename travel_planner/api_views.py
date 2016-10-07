from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import routers, serializers, viewsets
from rest_framework import status
from rest_framework.response import Response

from travel_planner.models import Trip


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'password', 'email')


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    serializer_class = UserSerializer

    @staticmethod
    def create(request):
        if get_user_model().objects.filter(username=request.POST['username']).count():
            return Response({}, status=status.HTTP_409_CONFLICT)
        user = get_user_model().objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password']
        )
        return Response({"username": user.username}, status=status.HTTP_201_CREATED)

    @staticmethod
    def perform_create(serializer):
        serializer.save()


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
router.register(r'user', UserViewSet, "user")
