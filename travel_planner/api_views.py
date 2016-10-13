import django_filters
from django.contrib.auth import get_user_model
from django.contrib.auth import views
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import exceptions
from rest_framework import filters
from rest_framework import permissions
from rest_framework import routers, serializers, viewsets
from rest_framework import status
from rest_framework.fields import DateField
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from travel_planner.models import Trip


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email')


class UserViewPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in {"POST", "PUT", "PATCH"} or (request.user and request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        if obj.is_staff or obj.is_superuser:
            return request.user.is_superuser
        else:
            return request.user == obj or (request.user.is_staff or request.user.is_superuser)


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserViewPermission,)

    def create(self, request, *args, **kwargs):
        if request.POST.get("time_zone"):
            request.session['time_zone'] = int(request.POST.get("time_zone"))

        if 'username' not in request.POST or 'password' not in request.POST:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
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

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(self, request, *args, **kwargs)
        except Http404:
            return Response(status=status.HTTP_204_NO_CONTENT)


class UserTripPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner or request.user.is_superuser


class TripSerializer(serializers.HyperlinkedModelSerializer):
    start_date = DateField(allow_null=True)
    end_date = DateField(allow_null=True)
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ('id', 'url', 'destination', 'start_date', 'end_date', 'days_left', 'comment')
        owner = serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            lookup_field='id',
            many=True,
            read_only=True
        )

    def get_days_left(self, obj):
        if self.context['request'].session.get('time_zone'):
            time_zone = self.context['request'].session.get('time_zone') * 60 * 60
            return obj.days_left(time_zone)
        else:
            return obj.days_left()


class AllTripSerializer(TripSerializer):
    class Meta(TripSerializer.Meta):
        fields = ('id', 'url', 'owner', 'destination', 'start_date', 'end_date', 'days_left', 'comment')


class UserTripsFilter(filters.FilterSet):
    destination = django_filters.Filter(name="destination")
    min_start_date = django_filters.DateFilter(name="start_date", lookup_expr='gte')
    max_start_date = django_filters.DateFilter(name="start_date", lookup_expr='lte')
    min_end_date = django_filters.DateFilter(name="end_date", lookup_expr='gte')
    max_end_date = django_filters.DateFilter(name="end_date", lookup_expr='lte')

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
            return Trip.objects.filter(owner=self.request.user).order_by("-start_date")

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(self, request, *args, **kwargs)
        except Http404:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class AllUserTripsViewSet(UserTripsViewSet):
    """ Returns a list of the all upcoming trips ordered by start_date.
    """
    serializer_class = AllTripSerializer
    permission_classes = (IsSuperUser,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = UserTripsFilter

    def get_queryset(self):
        return Trip.objects.all()


router = routers.DefaultRouter()
router.register(r'user_trips', UserTripsViewSet, "trip")
router.register(r'user', UserViewSet, "user")
router.register(r'all_user_trips', AllUserTripsViewSet, "all_user_trips")
