from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser, ConfirmationCode



# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", 'email')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_staff', 'is_active')}),
        ('Personal info', {'fields': ('username',)}),
        ('Date information', {'fields': ('last_login',)}),
    )

admin.site.register(ConfirmationCode)