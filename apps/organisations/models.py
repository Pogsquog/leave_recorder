import secrets
from enum import StrEnum

from django.db import models
from django.utils.translation import gettext_lazy as _


class OrganisationRole(StrEnum):
    MEMBER = "member"
    ADMIN = "admin"

    @classmethod
    def choices(cls):
        return [(item.value, _(item.value.capitalize())) for item in cls]


class Organisation(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "organisations"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_members_leave_entries(self, start_date=None, end_date=None):
        from apps.leave.models import LeaveEntry

        user_ids = self.memberships.values_list("user_id", flat=True)
        queryset = LeaveEntry.objects.filter(user_id__in=user_ids)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset.select_related("user")


class OrganisationMembership(models.Model):
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="organisation_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=OrganisationRole.choices(),
        default=OrganisationRole.MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "organisation_memberships"
        unique_together = ["organisation", "user"]
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.user.username} @ {self.organisation.name}"


class Invite(models.Model):
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name="invites",
    )
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    invited_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="sent_invites",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invites"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invite to {self.organisation.name} for {self.email}"

    @property
    def is_expired(self):
        from django.utils import timezone

        return self.expires_at < timezone.now()

    @property
    def is_accepted(self):
        return self.accepted_at is not None

    def accept(self, user):
        from django.utils import timezone

        OrganisationMembership.objects.create(
            organisation=self.organisation,
            user=user,
            role=OrganisationRole.MEMBER,
        )
        self.accepted_at = timezone.now()
        self.save()
