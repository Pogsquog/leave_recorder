from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.api.models import APIKey
from apps.leave.models import LeaveEntry
from apps.organisations.models import Invite, Organisation, OrganisationMembership
from apps.users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "annual_leave_allowance", "week_start", "is_staff"]
    fieldsets = UserAdmin.fieldsets + (
        (
            "Leave Preferences",
            {
                "fields": (
                    "annual_leave_allowance",
                    "carryover_max",
                    "carryover_days",
                    "week_start",
                    "year_start_month",
                    "year_start_day",
                )
            },
        ),
    )


@admin.register(LeaveEntry)
class LeaveEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "date", "leave_type", "half_day"]
    list_filter = ["leave_type", "half_day", "user"]
    date_hierarchy = "date"
    ordering = ["-date"]


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]


@admin.register(OrganisationMembership)
class OrganisationMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "organisation", "role", "joined_at"]
    list_filter = ["role", "organisation"]
    ordering = ["-joined_at"]


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ["organisation", "email", "invited_by", "created_at", "is_accepted"]
    list_filter = ["organisation", "accepted_at"]
    ordering = ["-created_at"]


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "created_at", "last_used_at", "is_active"]
    list_filter = ["is_active", "user"]
    ordering = ["-created_at"]
