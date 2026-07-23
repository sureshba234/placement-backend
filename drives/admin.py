from django.contrib import admin
from .models import Drive, EligibilityRule


class EligibilityRuleInline(admin.StackedInline):
    model = EligibilityRule
    extra = 1


class DriveAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'status', 'application_deadline')
    list_filter = ('status',)
    inlines = [EligibilityRuleInline]


admin.site.register(Drive, DriveAdmin)