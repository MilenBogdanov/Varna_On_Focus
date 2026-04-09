from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Zone


class ZoneMapAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        zones = Zone.objects.all()
        data = []

        for zone in zones:
            data.append({
                'id': zone.id,
                'name': zone.name,
                'coordinates': zone.coordinates,
            })

        return Response(data)
