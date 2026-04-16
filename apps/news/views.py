import json

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


from .forms import NewsCreateForm
from .models import News, NewsZone, ZonePoint
from django.core.paginator import Paginator
from django.db.models import Q
from .models import NewsSourceType
from datetime import datetime
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from apps.accounts.decorators import admin_or_superadmin_required
from apps.audit.services import log_news_operation
from apps.core.choices import AuditOperationType

def _serialize_news_for_audit(news):
    zone_points = []
    zone = getattr(news, "zone", None)

    if zone:
        zone_points = [
            [float(point.latitude), float(point.longitude)]
            for point in zone.points.all().order_by("point_order")
        ]

    return {
        "title": news.title,
        "content": news.content,
        "source_type": news.source_type,
        "admin_id": news.admin_id,
        "zone_points": zone_points,
    }

# ---------------------------------------------------
# CREATE NEWS
# ---------------------------------------------------

@login_required
@admin_or_superadmin_required
def create_news(request):

    if request.method == "POST":

        form = NewsCreateForm(request.POST)
        polygon = request.POST.get("polygon")

        if form.is_valid():

            news = form.save(commit=False)
            news.admin = request.user
            news.save()

            if polygon:

                try:
                    points = json.loads(polygon)
                except json.JSONDecodeError:
                    points = []

                if len(points) >= 1:

                    zone = NewsZone.objects.create(
                        news=news,
                        name=f"news_zone_{news.id}"
                    )

                    for index, point in enumerate(points):
                        ZonePoint.objects.create(
                            zone=zone,
                            latitude=point[0],
                            longitude=point[1],
                            point_order=index
                        )

            news.refresh_from_db()
            log_news_operation(
                news,
                AuditOperationType.CREATE,
                new_data=_serialize_news_for_audit(news)
            )

            return redirect("news")

    else:
        form = NewsCreateForm()

    return render(
        request,
        "news/create_news.html",
        {"form": form}
    )


# ---------------------------------------------------
# NEWS LIST PAGE
# ---------------------------------------------------

def news_list_view(request):

    news = News.objects.all().order_by("-created_at")

    search = request.GET.get("search")
    type_filter = request.GET.get("type")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if search:
        news = news.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )

    if type_filter:
        news = news.filter(source_type=type_filter)

    # -------- DATE FILTER --------

    if from_date:
        from_date = datetime.strptime(from_date, "%Y-%m-%d")
        news = news.filter(created_at__gte=from_date)

    if to_date:
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
        news = news.filter(created_at__lte=to_date)

    paginator = Paginator(news, 6)

    page = request.GET.get("page")
    news_list = paginator.get_page(page)

    return render(
        request,
        "news/news.html",
        {
            "news_list": news_list,
            "source_types": NewsSourceType.choices,
            "today": now().date()
        }
    )

# ---------------------------------------------------
# MAP API
# ---------------------------------------------------

def news_map_api(request):

    news = News.objects.all()

    data = []

    for n in news:

        zone = NewsZone.objects.filter(news=n).first()

        coordinates = []

        if zone:

            points = ZonePoint.objects.filter(
                zone=zone
            ).order_by("point_order")

            coordinates = [
                [p.latitude, p.longitude]
                for p in points
            ]

        data.append({
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "coordinates": coordinates,
            "created_at": n.created_at.isoformat()
        })

    return JsonResponse(data, safe=False)


# ---------------------------------------------------
# EDIT NEWS
# ---------------------------------------------------

@login_required
@admin_or_superadmin_required
def edit_news(request, news_id):

    news = get_object_or_404(
        News.objects.select_related("zone").prefetch_related("zone__points"),
        id=news_id
    )

    points = []

    if hasattr(news, "zone") and news.zone:
        points = [
            [float(p.latitude), float(p.longitude)]
            for p in news.zone.points.all().order_by("point_order")
        ]

    if request.method == "POST":

        old_data = _serialize_news_for_audit(news)
        form = NewsCreateForm(request.POST, instance=news)
        polygon = request.POST.get("polygon")

        if form.is_valid():

            news = form.save()

            if not polygon:
                NewsZone.objects.filter(news=news).delete()
                news.refresh_from_db()
                new_data = _serialize_news_for_audit(news)
                if old_data != new_data:
                    log_news_operation(
                        news,
                        AuditOperationType.UPDATE,
                        old_data=old_data,
                        new_data=new_data
                    )
                return redirect("news")

            try:
                new_points = json.loads(polygon)
            except json.JSONDecodeError:
                new_points = []

            if len(new_points) == 0:
                NewsZone.objects.filter(news=news).delete()
                news.refresh_from_db()
                new_data = _serialize_news_for_audit(news)
                if old_data != new_data:
                    log_news_operation(
                        news,
                        AuditOperationType.UPDATE,
                        old_data=old_data,
                        new_data=new_data
                    )
                return redirect("news")

            zone, created = NewsZone.objects.get_or_create(
                news=news,
                defaults={"name": f"news_zone_{news.id}"}
            )

            ZonePoint.objects.filter(zone=zone).delete()

            for index, point in enumerate(new_points):
                ZonePoint.objects.create(
                    zone=zone,
                    latitude=float(point[0]),
                    longitude=float(point[1]),
                    point_order=index
                )

            news.refresh_from_db()
            new_data = _serialize_news_for_audit(news)

            if old_data != new_data:
                log_news_operation(
                    news,
                    AuditOperationType.UPDATE,
                    old_data=old_data,
                    new_data=new_data
                )

            return redirect("news")

    else:
        form = NewsCreateForm(instance=news)

    return render(
        request,
        "news/edit_news.html",
        {
            "form": form,
            "news": news,
            "points_json": json.dumps(points)  # 🔥 КЛЮЧОВО
        }
    )

# ---------------------------------------------------
# DELETE NEWS
# ---------------------------------------------------

@login_required
@admin_or_superadmin_required
def delete_news(request, news_id):

    news = get_object_or_404(News, id=news_id)
    old_data = _serialize_news_for_audit(news)

    log_news_operation(
        news,
        AuditOperationType.DELETE,
        old_data=old_data,
        new_data=None
    )

    news.delete()

    return redirect("news")