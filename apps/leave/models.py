from datetime import date, timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.dates import get_month_end_date, get_month_start_date


class LeaveType(models.TextChoices):
    VACATION = "vacation", _("Vacation")
    SICK = "sick", _("Sick")


class LeaveEntry(models.Model):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="leave_entries",
    )
    date = models.DateField(db_index=True)
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
        default=LeaveType.VACATION,
    )
    half_day = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leave_entries"
        ordering = ["date"]
        unique_together = ["user", "date"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "leave_type"]),
        ]

    def __str__(self):
        half = " (½)" if self.half_day else ""
        return f"{self.user.username} - {self.date}{half}"

    @classmethod
    def get_days_for_period(cls, user, start_date, end_date, leave_type=None):
        queryset = cls.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date,
        )
        if leave_type:
            queryset = queryset.filter(leave_type=leave_type)

        full_days = queryset.filter(half_day=False).count()
        half_days = queryset.filter(half_day=True).count()

        return full_days + (half_days * 0.5)


class LeaveCalculator:
    @staticmethod
    def get_year_stats(user, year=None):
        start_date = user.get_year_start_date(year)
        end_date = user.get_year_end_date(year)
        today = date.today()

        total_allowance = user.total_leave_allowance

        entries = LeaveEntry.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date,
        )

        taken_entries = entries.filter(date__lte=today)
        booked_entries = entries.filter(date__gt=today)

        taken_days = taken_entries.filter(half_day=False).count() + (taken_entries.filter(half_day=True).count() * 0.5)
        booked_days = booked_entries.filter(half_day=False).count() + (
            booked_entries.filter(half_day=True).count() * 0.5
        )

        remaining = total_allowance - taken_days - booked_days

        days_until_year_end = (end_date - today).days if today <= end_date else 0

        return {
            "total_allowance": total_allowance,
            "taken_days": taken_days,
            "booked_days": booked_days,
            "remaining_days": remaining,
            "days_until_year_end": days_until_year_end,
            "year_start": start_date,
            "year_end": end_date,
        }

    @staticmethod
    def get_month_data(user, year, month, additional_users=None):
        from calendar import monthcalendar

        start_date = get_month_start_date(year, month)
        end_date = get_month_end_date(year, month)

        all_users = [user]
        if additional_users:
            all_users.extend(additional_users)

        user_ids = [u.id for u in all_users]

        entries = {
            (entry.user_id, entry.date): entry
            for entry in LeaveEntry.objects.filter(
                user_id__in=user_ids,
                date__gte=start_date,
                date__lte=end_date,
            )
        }

        own_entries = {
            entry.date: entry
            for entry in LeaveEntry.objects.filter(
                user=user,
                date__gte=start_date,
                date__lte=end_date,
            )
        }

        weeks = monthcalendar(year, month)

        month_days = []
        for week in weeks:
            week_days = []
            for day_idx, day in enumerate(week):
                if day == 0:
                    week_days.append(None)
                else:
                    current_date = date(year, month, day)
                    other_entries = [
                        entries.get((uid, current_date))
                        for uid in user_ids
                        if uid != user.id and entries.get((uid, current_date))
                    ]
                    week_days.append(
                        {
                            "date": current_date,
                            "day": day,
                            "entry": own_entries.get(current_date),
                            "other_entries": other_entries,
                            "is_weekend": day_idx >= 5 if user.week_start == 1 else day_idx == 0 or day_idx == 6,
                            "is_today": current_date == date.today(),
                        }
                    )
            month_days.append(week_days)

        return {
            "year": year,
            "month": month,
            "weeks": month_days,
            "prev_month": get_month_start_date(year, month) - timedelta(days=1),
            "next_month": get_month_start_date(year + (1 if month == 12 else 0), (month % 12) + 1),
        }
