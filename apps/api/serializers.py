from rest_framework import serializers

from apps.leave.models import LeaveEntry
from apps.organisations.models import Invite, Organisation, OrganisationMembership
from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "annual_leave_allowance",
            "carryover_max",
            "carryover_days",
            "week_start",
            "year_start_month",
            "year_start_day",
        ]
        read_only_fields = ["id", "username"]


class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "annual_leave_allowance",
            "carryover_max",
            "carryover_days",
            "week_start",
            "year_start_month",
            "year_start_day",
        ]


class LeaveEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveEntry
        fields = ["id", "date", "leave_type", "half_day", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class LeaveStatsSerializer(serializers.Serializer):
    total_allowance = serializers.FloatField()
    taken_days = serializers.FloatField()
    booked_days = serializers.FloatField()
    remaining_days = serializers.FloatField()
    days_until_year_end = serializers.IntegerField()
    year_start = serializers.DateField()
    year_end = serializers.DateField()


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ["id", "name", "slug", "created_at"]
        read_only_fields = ["id", "created_at"]


class OrganisationMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = OrganisationMembership
        fields = ["id", "user", "role", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class InviteSerializer(serializers.ModelSerializer):
    organisation = OrganisationSerializer(read_only=True)

    class Meta:
        model = Invite
        fields = ["id", "organisation", "email", "created_at", "expires_at", "is_expired", "is_accepted"]
        read_only_fields = ["id", "created_at"]
