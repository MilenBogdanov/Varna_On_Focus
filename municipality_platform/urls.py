from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.news.views import news_map_api
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.signals.api_views import SignalViewSet, SignalMapAPIView
from apps.news.api_views import ZoneMapAPIView
from apps.core.views import map_view
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.views.generic import TemplateView
from apps.core.views import map_view, contact, admin_dashboard, super_admin_panel

# -------------------------
# API Router
# -------------------------
router = DefaultRouter()
router.register(r'signals', SignalViewSet, basename='signals')


# -------------------------
# URL Patterns
# -------------------------
urlpatterns = [

    # Root redirect към landing page
    path('', TemplateView.as_view(template_name='landing/landing.html'), name='index'),

    # Admin
    path('admin/', admin.site.urls),

    # -------------------------
    # JWT AUTH
    # -------------------------
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # -------------------------
    # API MAP DATA
    # -------------------------
    path("api/map/news/", news_map_api, name="news-map"),
    path('api/map/signals/', SignalMapAPIView.as_view(), name='signals-map'),
    path('api/map/zones/', ZoneMapAPIView.as_view(), name='zones-map'),

    # -------------------------
    # Pages
    # -------------------------
    path('map/', map_view, name='map'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('super-admin-panel/', super_admin_panel, name='super_admin_panel'),
    path('contact/', contact, name='contact'),

    # Signals app
    path('signals/', include('apps.signals.urls')),

    # Accounts app (register, verify-email, etc.)
    path('', include('apps.accounts.urls')),

    # Login / Logout
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path("news/", include("apps.news.urls")),
    # -------------------------
    # DRF Router
    # -------------------------
    path('', include(router.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)