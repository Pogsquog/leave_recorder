from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    WEEK_START_MONDAY = 1
    WEEK_START_SUNDAY = 0
    WEEK_START_CHOICES = [
        (WEEK_START_MONDAY, "Monday"),
        (WEEK_START_SUNDAY, "Sunday"),
    ]

    annual_leave_allowance = models.PositiveIntegerField(
        default=25,
        help_text="Number of annual leave days per year",
    )
    carryover_max = models.PositiveIntegerField(
        default=5,
        help_text="Maximum days that can be carried over from previous year",
    )
    carryover_days = models.PositiveIntegerField(
        default=0,
        help_text="Days carried over from previous year",
    )
    week_start = models.IntegerField(
        choices=WEEK_START_CHOICES,
        default=WEEK_START_MONDAY,
        help_text="First day of the week",
    )
    year_start_month = models.PositiveIntegerField(
        default=1,
        help_text="Month when the leave year starts (1=January, 4=April, etc.)",
    )
    year_start_day = models.PositiveIntegerField(
        default=1,
        help_text="Day of month when the leave year starts",
    )

    class Meta:
        db_table = "users"
        ordering = ["username"]

    def __str__(self):
        return self.username

    @property
    def total_leave_allowance(self):
        return self.annual_leave_allowance + self.carryover_days

    def get_year_start_date(self, year=None):
        from datetime import date

        if year is None:
            today = date.today()
            year = today.year
            candidate = date(year, self.year_start_month, self.year_start_day)
            if today < candidate:
                year -= 1

        return date(year, self.year_start_month, self.year_start_day)

    def get_year_end_date(self, year=None):
        from datetime import date, timedelta

        start = self.get_year_start_date(year)
        return date(start.year + 1, start.month, start.day) - timedelta(days=1)
