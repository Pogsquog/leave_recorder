from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView

from .forms import InviteForm, OrganisationForm
from .models import Invite, Organisation, OrganisationMembership, OrganisationRole


class OrganisationListView(ListView):
    model = Organisation
    template_name = "organisation/list.html"
    context_object_name = "organisations"

    def get_queryset(self):
        user_orgs = self.request.user.organisation_memberships.values_list("organisation_id", flat=True)
        return Organisation.objects.filter(id__in=user_orgs)


class OrganisationDetailView(DetailView):
    model = Organisation
    template_name = "organisation/detail.html"
    context_object_name = "organisation"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        user_orgs = self.request.user.organisation_memberships.values_list("organisation_id", flat=True)
        return Organisation.objects.filter(id__in=user_orgs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membership"] = self.request.user.organisation_memberships.filter(organisation=self.object).first()
        context["members"] = self.object.memberships.select_related("user")
        context["invite_form"] = InviteForm()
        return context


class OrganisationCreateView(CreateView):
    model = Organisation
    form_class = OrganisationForm
    template_name = "organisation/form.html"

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            OrganisationMembership.objects.create(
                organisation=self.object,
                user=self.request.user,
                role=OrganisationRole.ADMIN,
            )
        return response


@login_required
def invite_member(request: HttpRequest, slug: str) -> HttpResponse:
    organisation = get_object_or_404(
        Organisation,
        slug=slug,
        memberships__user=request.user,
        memberships__role=OrganisationRole.ADMIN,
    )

    if request.method == "POST":
        form = InviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            Invite.objects.create(
                organisation=organisation,
                email=email,
                invited_by=request.user,
                expires_at=timezone.now() + timedelta(days=7),
            )
            messages.success(request, f"Invitation sent to {email}")
    return redirect("organisations:detail", slug=slug)


@login_required
def accept_invite(request: HttpRequest, token: str) -> HttpResponse:
    invite = get_object_or_404(Invite, token=token)

    if invite.is_expired:
        messages.error(request, "This invitation has expired.")
        return redirect("leave:month")

    if invite.is_accepted:
        messages.info(request, "This invitation has already been accepted.")
        return redirect("leave:month")

    if request.user.email != invite.email:
        messages.error(
            request,
            f"This invitation was sent to {invite.email}, but you are logged in as {request.user.email}.",
        )
        return redirect("leave:month")

    invite.accept(request.user)
    messages.success(request, f"You have joined {invite.organisation.name}!")
    return redirect("organisations:detail", slug=invite.organisation.slug)


@login_required
def org_leave_view(request: HttpRequest, slug: str) -> HttpResponse:
    from datetime import date

    from apps.leave.models import LeaveCalculator

    organisation = get_object_or_404(
        Organisation,
        slug=slug,
        memberships__user=request.user,
    )

    today = date.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    entries = organisation.get_members_leave_entries(start_date, end_date).select_related("user")

    member_stats = {}
    for membership in organisation.memberships.select_related("user"):
        member_stats[membership.user.id] = LeaveCalculator.get_year_stats(membership.user, year)

    entries_by_date = {}
    for entry in entries:
        if entry.date not in entries_by_date:
            entries_by_date[entry.date] = []
        entries_by_date[entry.date].append(entry)

    context = {
        "organisation": organisation,
        "entries_by_date": entries_by_date,
        "member_stats": member_stats,
        "year": year,
        "month": month,
    }
    return render(request, "organisation/leave_view.html", context)
