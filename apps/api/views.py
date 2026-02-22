from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.leave.models import LeaveCalculator, LeaveEntry
from apps.organisations.models import Organisation, OrganisationMembership

from .authentication import APIKey
from .serializers import (
    APIKeyCreateResponseSerializer,
    APIKeySerializer,
    LeaveEntrySerializer,
    LeaveStatsSerializer,
    OrganisationMembershipSerializer,
    OrganisationSerializer,
    UserPreferencesSerializer,
    UserSerializer,
)


@extend_schema_view(
    list=extend_schema(
        description="List all leave entries for the authenticated user.",
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="Filter by start date (ISO format: YYYY-MM-DD)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="end_date",
                description="Filter by end date (ISO format: YYYY-MM-DD)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="leave_type",
                description="Filter by leave type (vacation or sick)",
                required=False,
                type=str,
                enum=["vacation", "sick"],
            ),
        ],
    ),
    create=extend_schema(
        description="Create a new leave entry for the authenticated user.",
    ),
    retrieve=extend_schema(
        description="Retrieve a specific leave entry.",
    ),
    update=extend_schema(
        description="Update a specific leave entry.",
    ),
    partial_update=extend_schema(
        description="Partially update a specific leave entry.",
    ),
    destroy=extend_schema(
        description="Delete a specific leave entry.",
    ),
)
class LeaveEntryViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> "LeaveEntry.objects.QuerySet":
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

    def perform_create(self, serializer: LeaveEntrySerializer) -> None:
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    @extend_schema(
        description="Get leave statistics for the authenticated user.",
        parameters=[
            OpenApiParameter(
                name="year",
                description="Filter by year (defaults to current year)",
                required=False,
                type=int,
            ),
        ],
        responses={200: LeaveStatsSerializer},
    )
    def stats(self, request: Request) -> Response:
        year = request.query_params.get("year")
        if year:
            year = int(year)
        stats = LeaveCalculator.get_year_stats(request.user, year)
        serializer = LeaveStatsSerializer(stats)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        description="List all organisations the authenticated user is a member of.",
    ),
    retrieve=extend_schema(
        description="Retrieve details of a specific organisation.",
    ),
)
class OrganisationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> "Organisation.objects.QuerySet":
        user_orgs = OrganisationMembership.objects.filter(user=self.request.user).values_list(
            "organisation_id", flat=True
        )
        return Organisation.objects.filter(id__in=user_orgs)

    @action(detail=True, methods=["get"])
    @extend_schema(
        description="Get all members of a specific organisation.",
        responses={200: OrganisationMembershipSerializer(many=True)},
    )
    def members(self, request: Request, pk: int | None = None) -> Response:
        organisation = self.get_object()
        memberships = OrganisationMembership.objects.filter(organisation=organisation)
        serializer = OrganisationMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    @extend_schema(
        description="Get leave entries for all members of a specific organisation.",
        parameters=[
            OpenApiParameter(
                name="start_date",
                description="Filter by start date (ISO format: YYYY-MM-DD)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="end_date",
                description="Filter by end date (ISO format: YYYY-MM-DD)",
                required=False,
                type=str,
            ),
        ],
        responses={200: LeaveEntrySerializer(many=True)},
    )
    def leave_entries(
        self,
        request: Request,
        pk: int | None = None,
    ) -> Response:
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


@extend_schema(
    description="Get or update the authenticated user's profile.",
    methods=["GET", "PATCH"],
)
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def current_user(request: Request) -> Response:
    if request.method == "GET":
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    elif request.method == "PATCH":
        serializer = UserPreferencesSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description="Manage API keys for the authenticated user.",
    methods=["GET", "POST", "DELETE"],
    responses={
        "GET": APIKeySerializer(many=True),
        "POST": APIKeyCreateResponseSerializer,
        "DELETE": None,
    },
    request={
        "POST": {"type": "object", "properties": {"name": {"type": "string"}}},
        "DELETE": {"type": "object", "properties": {"id": {"type": "integer"}}},
    },
)
@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def api_keys(request: Request) -> Response:
    if request.method == "GET":
        keys = APIKey.objects.filter(user=request.user)
        serializer = APIKeySerializer(keys, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        name = request.data.get("name", "")
        key = APIKey.objects.create(user=request.user, name=name)
        return Response(
            {
                "id": key.id,
                "key": key.key,
                "name": key.name,
                "created_at": key.created_at,
                "last_used_at": key.last_used_at,
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
