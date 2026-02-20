from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.leave.models import LeaveCalculator, LeaveEntry
from apps.organisations.models import Organisation, OrganisationMembership

from .authentication import APIKey
from .serializers import (
    LeaveEntrySerializer,
    LeaveStatsSerializer,
    OrganisationMembershipSerializer,
    OrganisationSerializer,
    UserPreferencesSerializer,
    UserSerializer,
)


class LeaveEntryViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = LeaveEntry.objects.filter(user=self.request.user)

        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        leave_type = self.request.query_params.get("leave_type")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if leave_type:
            queryset = queryset.filter(leave_type=leave_type)

        return queryset.order_by("date")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        year = request.query_params.get("year")
        if year:
            year = int(year)
        stats = LeaveCalculator.get_year_stats(request.user, year)
        serializer = LeaveStatsSerializer(stats)
        return Response(serializer.data)


class OrganisationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_orgs = OrganisationMembership.objects.filter(user=self.request.user).values_list(
            "organisation_id", flat=True
        )
        return Organisation.objects.filter(id__in=user_orgs)

    @action(detail=True, methods=["get"])
    def members(self, request, pk=None):
        organisation = self.get_object()
        memberships = OrganisationMembership.objects.filter(organisation=organisation)
        serializer = OrganisationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def leave_entries(self, request, pk=None):
        from datetime import date

        organisation = self.get_object()
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            start_date = date.fromisoformat(start_date)
        if end_date:
            end_date = date.fromisoformat(end_date)

        entries = organisation.get_members_leave_entries(start_date, end_date)
        serializer = LeaveEntrySerializer(entries, many=True)
        return Response(serializer.data)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def current_user(request):
    if request.method == "GET":
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    elif request.method == "PATCH":
        serializer = UserPreferencesSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def api_keys(request):
    if request.method == "GET":
        keys = APIKey.objects.filter(user=request.user)
        data = [{"id": k.id, "name": k.name, "created_at": k.created_at, "last_used_at": k.last_used_at} for k in keys]
        return Response(data)

    elif request.method == "POST":
        name = request.data.get("name", "")
        key = APIKey.objects.create(user=request.user, name=name)
        return Response(
            {
                "id": key.id,
                "key": key.key,
                "name": key.name,
                "warning": "Save this key securely. It will not be shown again.",
            },
            status=status.HTTP_201_CREATED,
        )

    elif request.method == "DELETE":
        key_id = request.data.get("id")
        if not key_id:
            return Response({"error": "id required"}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = APIKey.objects.filter(id=key_id, user=request.user).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Key not found"}, status=status.HTTP_404_NOT_FOUND)
