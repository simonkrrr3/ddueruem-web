from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin import ModelAdmin
from core.fileupload.models import File
from core.user.forms import AdminUserChangeForm, AdminUserCreationForm
from core.user.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.templatetags.admin_list import _boolean_icon
from ddueruemweb.settings import PASSWORD_RESET_TIMEOUT_DAYS


class UserAdmin(BaseUserAdmin):
    """
    Class for defining the backend user admin panel, its used forms and which data should be displayed.
    """
    model = User
    form = AdminUserChangeForm
    add_form = AdminUserCreationForm
    # Show attributes in overall list view
    list_display = ('id', 'email', 'institute', 'is_active_ex', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
    list_filter = ('institute', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined')
    # Define which (and how) attributes should be displayed when clicking on a certain user
    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('Personal Information', {'fields': ['institute', 'bio']}),
        # groups and user_permissions come from PermissionsMixin
        ('Permissions', {'fields': ['is_staff', 'is_active', 'groups', 'user_permissions']}),
        ('Important dates', {'fields': ['last_login', 'date_joined']})
    ]
    readonly_fields = ('date_joined',)
    # add_fieldsets is not a standard ModelAdmin attribute.
    # UserAdmin overrides get_fieldsets to use this attribute when creating a user.
    # otherwise, it would throw the following error when trying to add a new user
    # "The value of 'ordering[0]' refers to 'username', which is not an attribute of 'core_user.User'"
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    @staticmethod
    def is_active_ex(user):
        """
        Extended is_active attribute which either is true or returns
        how much time is left (Hh:Mm:Ss) until the activation period ends.
        :return:
        """

        delta = (user.date_joined + timedelta(days=PASSWORD_RESET_TIMEOUT_DAYS)) - timezone.now()
        total_minute, second = divmod(delta.seconds, 60)
        hour, minute = divmod(total_minute, 60)

        return _boolean_icon(True) if user.is_active else f"{delta.days}d{hour}h{minute:02}m{second:02}s"


class FileAdmin(ModelAdmin):
    """
    Class for defining the backend file admin panel and which data should be displayed.
    """
    model = File
    # Show attributes in list view
    list_display = ('id', 'file', 'owner', 'uploaded_at')
    # list_filter = ('is_superuser',)
    # Define how view should look like after clicking on an email
    fieldsets = [
        (None, {'fields': ['owner']}),
        ('Information', {'fields': ['description', 'file', 'license']}),
        ('Important dates', {'fields': ['uploaded_at']})
    ]
    readonly_fields = ('uploaded_at',)
    search_fields = ('owner',)
    ordering = ('owner', 'uploaded_at')
    filter_horizontal = ()


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(File, FileAdmin)
