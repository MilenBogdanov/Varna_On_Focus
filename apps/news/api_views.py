from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.core.models import Zone
from .models import News

class ZoneMapAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        zones = Zone.objects.all()
        data = []

        for zone in zones:
            data.append({
                'id': zone.id,
                'name': zone.name,
                'coordinates': zone.coordinates  # JSON поле
            })

        return Response(data)

class NewsMapAPIView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):

        news_items = News.objects.select_related("zone").prefetch_related(
            "zone__points"
        )

        data = []

        for news in news_items:

            if not hasattr(news, "zone"):
                continue

            points = news.zone.points.all().order_by("point_order")

            coordinates = []

            for p in points:
                coordinates.append([
                    float(p.latitude),
                    float(p.longitude)
                ])

            data.append({
                "id": news.id,
                "title": news.title,
                "content": news.content,
                "created_at": news.created_at.isoformat(),
                "coordinates": coordinates
            })

        return Response(data)