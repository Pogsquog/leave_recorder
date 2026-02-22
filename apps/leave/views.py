from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import LeaveEntryForm
from .models import LeaveCalculator, LeaveEntry

MAX_RANGE_DAYS = 365


@login_required
def month_view(
    request: HttpRequest,
    year: int | None = None,
    month: int | None = None,
) -> HttpResponse:
    today = date.today()
    year = year or today.year
    month = month or today.month

    user = request.user
    from django.contrib.auth import get_user_model

    User = get_user_model()

    additional_user_ids = request.GET.getlist("users")
    additional_users = []
    if additional_user_ids:
        from apps.organisations.models import OrganisationMembership

        org_member_ids = (
            OrganisationMembership.objects.filter(user=user)
            .values_list("organisation__memberships__user_id", flat=True)
            .distinct()
        )

        for uid_str in additional_user_ids:
            try:
                uid = int(uid_str)
                if uid in org_member_ids and uid != user.id:
                    additional_users.append(User.objects.get(id=uid))
            except (ValueError, User.DoesNotExist):
                pass

    month_data = LeaveCalculator.get_month_data(user, year, month, additional_users)
    year_stats = LeaveCalculator.get_year_stats(user)

    context = {
        "month_data": month_data,
        "year_stats": year_stats,
        "week_start": user.week_start,
        "selected_user_ids": [u.id for u in additional_users],
    }

    if user.organisation_memberships.exists():
        from apps.organisations.models import OrganisationMembership

        org_ids = user.organisation_memberships.values_list("organisation_id", flat=True)
        org_members = (
            User.objects.filter(organisation_memberships__organisation_id__in=org_ids).exclude(id=user.id).distinct()
        )
        context["org_members"] = org_members

    return render(request, "leave/month.html", context)


@login_required
@require_POST
def add_entry(request: HttpRequest) -> HttpResponse:
    form = LeaveEntryForm(request.POST)
    if form.is_valid():
        entry = form.save(commit=False)
        entry.user = request.user
        entry.save()
        messages.success(request, "Leave entry added.")
    else:
        messages.error(request, "Failed to add leave entry.")
    return redirect("leave:month")


@login_required
@require_POST
def toggle_entry(request: HttpRequest) -> JsonResponse:
    date_str = request.POST.get("date")
    leave_type = request.POST.get("leave_type", "vacation")
    half_day = request.POST.get("half_day") == "true"
    cycle = request.POST.get("cycle") == "true"

    try:
        entry_date = date.fromisoformat(date_str)
    except ValueError:
        return JsonResponse({"error": "Invalid date"}, status=400)

    if cycle:
        entry = LeaveEntry.objects.filter(user=request.user, date=entry_date).first()

        if not entry:
            LeaveEntry.objects.create(user=request.user, date=entry_date, leave_type=leave_type, half_day=False)
            return JsonResponse({"created": True, "half_day": False, "leave_type": leave_type})
        elif not entry.half_day:
            entry.half_day = True
            entry.save()
            return JsonResponse({"created": False, "half_day": True, "leave_type": entry.leave_type})
        else:
            entry.delete()
            return JsonResponse({"deleted": True})

    entry, created = LeaveEntry.objects.get_or_create(
        user=request.user,
        date=entry_date,
        defaults={"leave_type": leave_type, "half_day": half_day},
    )

    if not created:
        if entry.leave_type != leave_type:
            entry.leave_type = leave_type
            entry.half_day = half_day
            entry.save()
        elif entry.half_day != half_day:
            entry.half_day = half_day
            entry.save()
        else:
            entry.delete()
            return JsonResponse({"deleted": True})

    return JsonResponse(
        {
            "created": created,
            "half_day": entry.half_day,
            "leave_type": entry.leave_type,
        }
    )


@login_required
@require_http_methods(["DELETE"])
def delete_entry(request: HttpRequest, entry_id: int) -> HttpResponse:
    entry = get_object_or_404(LeaveEntry, id=entry_id, user=request.user)
    entry.delete()
    messages.success(request, "Leave entry deleted.")
    return redirect("leave:month")


@login_required
@require_POST
def add_range(request: HttpRequest) -> JsonResponse:
    start_date_str = request.POST.get("start_date")
    end_date_str = request.POST.get("end_date")
    leave_type = request.POST.get("leave_type", "vacation")
    half_day = request.POST.get("half_day") == "true"

    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except ValueError:
        return JsonResponse({"error": "Invalid date format"}, status=400)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    if (end_date - start_date).days > MAX_RANGE_DAYS:
        return JsonResponse({"error": f"Maximum range is {MAX_RANGE_DAYS} days"}, status=400)

    created_count = 0
    current = start_date
    while current <= end_date:
        entry, created = LeaveEntry.objects.get_or_create(
            user=request.user,
            date=current,
            defaults={"leave_type": leave_type, "half_day": half_day},
        )
        if created:
            created_count += 1
        current += timedelta(days=1)

    return JsonResponse({"created": created_count})


@login_required
def entry_detail(request: HttpRequest, entry_id: int) -> HttpResponse:
    entry = get_object_or_404(LeaveEntry, id=entry_id, user=request.user)
    return render(request, "leave/entry_detail.html", {"entry": entry})
