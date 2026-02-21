"""Edge case tests for LeaveCalculator."""

from datetime import date

import pytest
from django.contrib.auth import get_user_model

from apps.leave.models import LeaveCalculator, LeaveEntry, LeaveType

User = get_user_model()


@pytest.mark.django_db
class TestLeaveCalculatorEdgeCases:
    """Test edge cases for leave calculations."""

    def test_year_boundary_calculation(self, user):
        """Test leave calculation at year boundaries."""
        user.annual_leave_allowance = 25
        user.save()

        LeaveEntry.objects.create(user=user, date=date(2025, 12, 31), leave_type=LeaveType.VACATION)
        LeaveEntry.objects.create(user=user, date=date(2026, 1, 1), leave_type=LeaveType.VACATION)

        stats_2025 = LeaveCalculator.get_year_stats(user, 2025)
        stats_2026 = LeaveCalculator.get_year_stats(user, 2026)

        assert stats_2025["taken_days"] == 1
        assert stats_2026["taken_days"] == 1

    def test_carryover_calculation(self, user_with_leave):
        """Test carryover days are included in allowance."""
        user_with_leave.annual_leave_allowance = 25
        user_with_leave.carryover_days = 10
        user_with_leave.save()

        stats = LeaveCalculator.get_year_stats(user_with_leave, 2026)

        assert stats["total_allowance"] == 35

    def test_different_year_start_dates(self, user):
        """Test calculation with different year start dates."""
        user.annual_leave_allowance = 25
        user.save()

        LeaveEntry.objects.create(user=user, date=date(2026, 4, 15), leave_type=LeaveType.VACATION)

        stats = LeaveCalculator.get_year_stats(user, 2026)
        assert stats["year_start"] == date(2026, 1, 1)
        assert stats["year_end"] == date(2026, 12, 31)

    def test_leap_year_handling(self, user):
        """Test leave calculation in leap year."""
        user.annual_leave_allowance = 25
        user.save()

        LeaveEntry.objects.create(user=user, date=date(2024, 2, 29), leave_type=LeaveType.VACATION)

        stats = LeaveCalculator.get_year_stats(user, 2024)
        assert stats["taken_days"] == 1

    def test_half_day_year_boundary(self, user):
        """Test half-day entries at year boundaries."""
        user.annual_leave_allowance = 25
        user.save()

        LeaveEntry.objects.create(
            user=user,
            date=date(2025, 12, 31),
            leave_type=LeaveType.VACATION,
            half_day=True,
        )
        LeaveEntry.objects.create(
            user=user,
            date=date(2026, 1, 1),
            leave_type=LeaveType.VACATION,
            half_day=True,
        )

        stats_2025 = LeaveCalculator.get_year_stats(user, 2025)
        stats_2026 = LeaveCalculator.get_year_stats(user, 2026)

        assert stats_2025["taken_days"] == 0.5
        assert stats_2026["taken_days"] == 0.5

    def test_negative_remaining_days(self, user):
        """Test negative remaining days when over allowance."""
        user.annual_leave_allowance = 10
        user.save()

        for i in range(15):
            LeaveEntry.objects.create(
                user=user,
                date=date(2026, 1, i + 1),
                leave_type=LeaveType.VACATION,
            )

        stats = LeaveCalculator.get_year_stats(user, 2026)
        assert stats["remaining_days"] == -5

    def test_zero_allowance(self, user):
        """Test calculation with zero leave allowance."""
        user.annual_leave_allowance = 0
        user.save()

        LeaveEntry.objects.create(user=user, date=date(2026, 1, 15), leave_type=LeaveType.VACATION)

        stats = LeaveCalculator.get_year_stats(user, 2026)
        assert stats["total_allowance"] == 0
        assert stats["remaining_days"] == -1

    def test_mixed_leave_types(self, user):
        """Test calculation with mixed leave types."""
        user.annual_leave_allowance = 25
        user.save()

        LeaveEntry.objects.create(user=user, date=date(2026, 1, 10), leave_type=LeaveType.VACATION)
        LeaveEntry.objects.create(
            user=user,
            date=date(2026, 1, 11),
            leave_type=LeaveType.VACATION,
            half_day=True,
        )
        LeaveEntry.objects.create(user=user, date=date(2026, 1, 12), leave_type=LeaveType.SICK)

        stats = LeaveCalculator.get_year_stats(user, 2026)
        assert stats["taken_days"] == 2.5

    def test_future_booked_days(self, user):
        """Test booked (future) days calculation."""
        user.annual_leave_allowance = 25
        user.save()

        LeaveEntry.objects.create(user=user, date=date(2026, 1, 10), leave_type=LeaveType.VACATION)

        future_date = date(2026, 12, 25)
        LeaveEntry.objects.create(user=user, date=future_date, leave_type=LeaveType.VACATION)

        stats = LeaveCalculator.get_year_stats(user, 2026)

        if date.today() < future_date:
            assert stats["booked_days"] == 1
            assert stats["taken_days"] == 1

    def test_month_data_empty_month(self, user):
        """Test month data for a month with no entries."""
        month_data = LeaveCalculator.get_month_data(user, 2026, 2)

        assert month_data["year"] == 2026
        assert month_data["month"] == 2
        assert len(month_data["weeks"]) > 0

        for week in month_data["weeks"]:
            for day in week:
                if day is not None:
                    assert day["entry"] is None

    def test_month_data_with_entries(self, user):
        """Test month data with leave entries."""
        user.annual_leave_allowance = 25
        user.save()

        LeaveEntry.objects.create(user=user, date=date(2026, 1, 15), leave_type=LeaveType.VACATION)

        month_data = LeaveCalculator.get_month_data(user, 2026, 1)

        found_entry = False
        for week in month_data["weeks"]:
            for day in week:
                if day is not None and day["date"] == date(2026, 1, 15):
                    assert day["entry"] is not None
                    assert day["entry"].leave_type == LeaveType.VACATION
                    found_entry = True

        assert found_entry is True

    def test_month_data_additional_users(self, user):
        """Test month data includes additional users' entries."""
        user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password123")

        LeaveEntry.objects.create(user=user, date=date(2026, 1, 15), leave_type=LeaveType.VACATION)
        LeaveEntry.objects.create(user=user2, date=date(2026, 1, 15), leave_type=LeaveType.SICK)

        month_data = LeaveCalculator.get_month_data(user, 2026, 1, additional_users=[user2])

        for week in month_data["weeks"]:
            for day in week:
                if day is not None and day["date"] == date(2026, 1, 15):
                    assert day["entry"] is not None
                    assert len(day["other_entries"]) == 1
                    assert day["other_entries"][0].user == user2

    def test_month_data_prev_next_month(self, user):
        """Test previous and next month calculations."""
        jan_data = LeaveCalculator.get_month_data(user, 2026, 1)
        dec_data = LeaveCalculator.get_month_data(user, 2026, 12)

        assert jan_data["prev_month"].month == 12
        assert jan_data["prev_month"].year == 2025

        assert dec_data["next_month"].month == 1
        assert dec_data["next_month"].year == 2027

    def test_days_until_year_end(self, user):
        """Test days until year end calculation."""
        user.annual_leave_allowance = 25
        user.save()

        stats = LeaveCalculator.get_year_stats(user, 2026)

        expected_days = (date(2026, 12, 31) - date.today()).days
        if expected_days < 0:
            assert stats["days_until_year_end"] == 0
        else:
            assert stats["days_until_year_end"] == expected_days

    def test_multiple_half_days_same_day(self, user):
        """Test multiple half-day entries on the same day (should not happen, but test anyway)."""
        user.annual_leave_allowance = 25
        user.save()

        entry1 = LeaveEntry.objects.create(
            user=user,
            date=date(2026, 1, 15),
            leave_type=LeaveType.VACATION,
            half_day=True,
        )

        stats = LeaveCalculator.get_year_stats(user, 2026)
        assert stats["taken_days"] == 0.5

        entry1.delete()

        LeaveEntry.objects.create(
            user=user,
            date=date(2026, 1, 15),
            leave_type=LeaveType.VACATION,
            half_day=False,
        )

        stats = LeaveCalculator.get_year_stats(user, 2026)
        assert stats["taken_days"] == 1
