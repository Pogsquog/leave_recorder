"""Template tags for calendar rendering."""

from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.simple_tag
def get_weekday_name(day_number: int, week_start: int = 1) -> str:
    """
    Get translated weekday name based on week start preference.

    Args:
        day_number: Day number (1-7)
        week_start: Week start day (1=Monday, 0=Sunday)

    Returns:
        Translated weekday abbreviation

    """
    days_monday_start = [_("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Sun")]
    days_sunday_start = [_("Sun"), _("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat")]

    if week_start == 1:
        return days_monday_start[day_number - 1]
    return days_sunday_start[day_number - 1]
