import django_filters
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import exceptions
from rest_framework import filters
from rest_framework import permissions
from rest_framework import routers, serializers, viewsets
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import views
from rest_framework.response import Response

from travel_planner.models import Trip


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'password', 'email')


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.none()
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = (AllowAny,)

    @staticmethod
    def create(request):
        if get_user_model().objects.filter(username=request.POST['username']).count():
            return Response({}, status=status.HTTP_409_CONFLICT)
        if request.POST.get('password-confirm') and request.POST['password'] != request.POST['password-confirm']:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.create_user(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if request.GET.get('next'):
            request._request.POST = request.POST
            return views.login(request._request)
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


class UserTripsFilter(filters.FilterSet):
    min_price = django_filters.Filter(name="dest")
    min_start_date = django_filters.DateFilter(name="start_date", lookup_expr='gte')
    max_start_date = django_filters.DateFilter(name="start_date", lookup_expr='lte')

    class Meta:
        model = Trip
        fields = ('destination', 'start_date', 'end_date', 'comment')


class UserTripsViewSet(viewsets.ModelViewSet):
    """ Returns a list of the current logged in user's upcoming trips ordered by start_date.
    """
    serializer_class = TripSerializer
    permission_classes = (UserTripPermission,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = UserTripsFilter

    def get_queryset(self):
        if self.request.user.is_anonymous:
            raise exceptions.PermissionDenied("Not logged in.")
        else:
            return Trip.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


router = routers.DefaultRouter()
router.register(r'user_trips', UserTripsViewSet, "trip")
router.register(r'user', UserViewSet, "user")
