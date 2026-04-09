from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import CommentSerializer
from .models import Comment
from .serializers import SignalImageSerializer
from .models import SignalImage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from apps.accounts.permissions import is_admin_or_superadmin

from .models import Signal
from .serializers import (
    SignalListSerializer,
    SignalDetailSerializer,
    SignalCreateSerializer,
)
from apps.accounts.drf_permissions import (
    IsAuthenticatedCitizen,
    IsAdminOrSuperAdmin,
    ReadOnlyForGuests,
)
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class SignalViewSet(ModelViewSet):
    queryset = Signal.objects.all().order_by('-created_at')
    permission_classes = [ReadOnlyForGuests]
    parser_classes = (MultiPartParser, FormParser)

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['title', 'description', 'address']

    def get_serializer_class(self):
        if self.action == 'list':
            return SignalListSerializer
        if self.action == 'retrieve':
            return SignalDetailSerializer
        if self.action == 'create':
            return SignalCreateSerializer
        return SignalDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticatedCitizen()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminOrSuperAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticatedCitizen]
    )
    def add_comment(self, request, pk=None):
        signal = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, signal=signal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticatedCitizen],
        parser_classes=[MultiPartParser, FormParser],
    )
    def add_image(self, request, pk=None):
        signal = self.get_object()
        serializer = SignalImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(signal=signal)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SignalMapAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        signals = Signal.objects.all()

        data = []

        for signal in signals:

            can_manage = False

            if request.user.is_authenticated:
                if request.user.is_superuser:
                    can_manage = True
                elif hasattr(request.user, "role") and request.user.role:
                    if request.user.role.name == "MUNICIPAL_ADMIN":
                        can_manage = True

            data.append({
                'id': signal.id,
                'title': signal.title,
                'latitude': float(signal.latitude),
                'longitude': float(signal.longitude),
                'status': signal.status,
                'status_display': signal.get_status_display(),
                'category': signal.category.name,
                'created_at': signal.created_at.isoformat(),
                'user': signal.user.full_name,
                'can_manage': can_manage,
            })

        return Response(data)