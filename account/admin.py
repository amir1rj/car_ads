from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User, PendingUser, Token, Profile, Log


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 1


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["phone_number", "username", "is_admin", ]
    list_filter = ["is_admin", 'is_active', 'roles']
    inlines = [ProfileInline, ]
    fieldsets = [
        (None, {"fields": ["password", "username"]}),
        ("اظلاعات شخصی", {"fields": ["phone_number"]}),
        ("دسترسی ها", {"fields": ["is_admin", "groups", "verified", "is_active","is_superuser", "roles", 'user_permissions']}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["phone_number", 'username', "password1", "password2"],
            },
        ),
    ]
    search_fields = ["username", "phone_number", ]
    ordering = ["username", ]
    filter_horizontal = ['groups', 'user_permissions']


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
admin.site.register(Token)
admin.site.register(PendingUser)
admin.site.register(Profile)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ["user", "type","ip_address","browser"]
    list_filter = ["type","browser"]
    search_fields = ["ip_address",'user']
