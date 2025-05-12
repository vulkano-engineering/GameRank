from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import SitePassword, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(SitePassword)
class SitePasswordAdmin(admin.ModelAdmin):
    list_display = ('value', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


# Re-register UserAdmin with UserProfile inline
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
