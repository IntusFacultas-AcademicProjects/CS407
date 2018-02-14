from django.contrib import admin
from audition_management.models import (
    AuditionAccount, CastingAccount, Role, Tag, PerformanceEvent)
from django.contrib.auth.models import User


class AuditionAccountInline(admin.TabularInline):
    model = AuditionAccount


class CastingAccountInline(admin.TabularInline):
    model = CastingAccount


class TagInline(admin.TabularInline):
    model = Tag


class PerformanceEventInline(admin.TabularInline):
    model = PerformanceEvent


class RoleAdmin(admin.ModelAdmin):
    model = admin
    inlines = [
        TagInline,
        PerformanceEventInline
    ]


# class UserAdmin(admin.ModelAdmin):
#     model = admin
#     inlines = [
#         AuditionAccountInline,
#         CastingAccountInline,
#     ]


admin.site.register(Role, RoleAdmin)
admin.site.register(CastingAccount)
admin.site.register(AuditionAccount)
# Register your models here.
