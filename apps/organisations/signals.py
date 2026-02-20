from asgiref.sync import async_to_sync
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.leave.models import LeaveEntry
from apps.organisations.models import OrganisationMembership


@receiver(post_save, sender=LeaveEntry)
def leave_entry_saved(sender, instance, created, **kwargs):
    _notify_org_members(
        instance.user,
        "leave_update",
        {
            "action": "created" if created else "updated",
            "user_id": instance.user_id,
            "date": str(instance.date),
            "leave_type": instance.leave_type,
            "half_day": instance.half_day,
        },
    )


@receiver(post_delete, sender=LeaveEntry)
def leave_entry_deleted(sender, instance, **kwargs):
    _notify_org_members(
        instance.user,
        "leave_update",
        {
            "action": "deleted",
            "user_id": instance.user_id,
            "date": str(instance.date),
        },
    )


def _notify_org_members(user, message_type, data):
    try:
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer is None:
            return

        membership_org_ids = OrganisationMembership.objects.filter(user=user).values_list("organisation_id", flat=True)

        for org_id in membership_org_ids:
            org = OrganisationMembership.objects.filter(organisation_id=org_id).first()
            if org:
                group_name = f"org_{org.organisation.slug}"
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": message_type,
                        "data": data,
                    },
                )
    except Exception:
        pass
