from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from travel_planner.models import Trip

admin.site.register(Trip)


class RestrictedStaffAdmin(UserAdmin):
    """
    Inspired by:
    https://stackoverflow.com/questions/2297377/how-do-i-prevent-permission-escalation-in-django-admin-when-granting-user-chang
    """
    staff_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        # No permissions
        (_('Important dates'), {'fields': ('last_login', 'date_joined')})
    )

    def change_view(self, request, object_id, *args, **kwargs):
        if not request.user.is_superuser:
            if User.objects.get(id=object_id).is_staff:
                raise PermissionDenied
            else:
                self.fieldsets = self.staff_fieldsets
        return super().change_view(request, object_id, *args, **kwargs)


admin.site.unregister(User)
admin.site.register(User, RestrictedStaffAdmin)
