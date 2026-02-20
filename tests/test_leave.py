from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from apps.leave.models import LeaveCalculator, LeaveEntry, LeaveType

User = get_user_model()


@pytest.mark.django_db
class TestLeaveEntry:
    def test_create_leave_entry(self, user):
        entry = LeaveEntry.objects.create(
            user=user,
            date=date.today(),
            leave_type=LeaveType.VACATION,
            half_day=False,
        )
        assert entry.user == user
        assert entry.leave_type == LeaveType.VACATION
        assert not entry.half_day

    def test_unique_user_date(self, user):
        LeaveEntry.objects.create(user=user, date=date.today())
        with pytest.raises(IntegrityError):
            LeaveEntry.objects.create(user=user, date=date.today())

    def test_get_days_for_period(self, user):
        today = date.today()
        LeaveEntry.objects.create(user=user, date=today, half_day=False)
        LeaveEntry.objects.create(user=user, date=today + timedelta(days=1), half_day=True)
        LeaveEntry.objects.create(user=user, date=today + timedelta(days=2), half_day=False)

        days = LeaveEntry.get_days_for_period(user, today, today + timedelta(days=2))
        assert days == 2.5

    def test_get_days_by_type(self, user):
        today = date.today()
        LeaveEntry.objects.create(
            user=user,
            date=today,
            leave_type=LeaveType.VACATION,
            half_day=False,
        )
        LeaveEntry.objects.create(
            user=user,
            date=today + timedelta(days=1),
            leave_type=LeaveType.SICK,
            half_day=False,
        )

        vacation_days = LeaveEntry.get_days_for_period(
            user, today, today + timedelta(days=1), leave_type=LeaveType.VACATION
        )
        sick_days = LeaveEntry.get_days_for_period(user, today, today + timedelta(days=1), leave_type=LeaveType.SICK)

        assert vacation_days == 1
        assert sick_days == 1


@pytest.mark.django_db
class TestLeaveCalculator:
    def test_get_year_stats_no_leave(self, user):
        stats = LeaveCalculator.get_year_stats(user)
        assert stats["total_allowance"] == user.annual_leave_allowance + user.carryover_days
        assert stats["taken_days"] == 0
        assert stats["booked_days"] == 0
        assert stats["remaining_days"] == stats["total_allowance"]

    def test_get_year_stats_with_leave(self, user):
        user.annual_leave_allowance = 25
        user.carryover_days = 5
        user.save()

        today = date.today()
        past_date = today - timedelta(days=5)
        future_date = today + timedelta(days=5)

        LeaveEntry.objects.create(user=user, date=past_date, half_day=False)
        LeaveEntry.objects.create(user=user, date=future_date, half_day=True)

        stats = LeaveCalculator.get_year_stats(user)
        assert stats["taken_days"] == 1
        assert stats["booked_days"] == 0.5
        assert stats["remaining_days"] == 28.5

    def test_get_month_data(self, user):
        test_date = date(2024, 6, 15)
        LeaveEntry.objects.create(user=user, date=test_date, half_day=False)

        month_data = LeaveCalculator.get_month_data(user, 2024, 6)

        assert month_data["year"] == 2024
        assert month_data["month"] == 6
        assert len(month_data["weeks"]) > 0

        found_entry = False
        for week in month_data["weeks"]:
            for day_data in week:
                if day_data and day_data["date"] == test_date:
                    assert day_data["entry"] is not None
                    found_entry = True
        assert found_entry
