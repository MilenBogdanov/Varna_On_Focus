from django.contrib import admin
from .models import News
from .models import NewsZone, ZonePoint

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'source_type', 'admin', 'created_at')
    list_filter = ('source_type', 'created_at')
    search_fields = ('title', 'content')

@admin.register(NewsZone)
class NewsZoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'news')


@admin.register(ZonePoint)
class ZonePointAdmin(admin.ModelAdmin):
    list_display = ('id', 'zone', 'point_order', 'latitude', 'longitude')
    list_filter = ('zone',)