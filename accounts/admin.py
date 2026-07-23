from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Info', {
            'fields': (
                'role', 'phone_number', 'college', 'branch',
                'cgpa', 'backlog_count', 'graduation_year', 'company_name',
            )
        }),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')


admin.site.register(User, UserAdmin)

# Register your models here.
