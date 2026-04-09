from django.urls import path
from .views import create_signal, manage_signal
from . import views
from .views import signal_detail

app_name = 'signals'

urlpatterns = [
    path('create/', create_signal, name='create_signal'),
    path('my/', views.my_signals, name='my_signals'),
    path('edit/<int:pk>/', views.edit_signal, name='edit_signal'),
    path("<int:signal_id>/manage/", views.manage_signal, name="manage_signal"),
    path("<int:pk>/", signal_detail, name="signal_detail"),
    path('<int:pk>/delete/', views.delete_signal, name='delete_signal'),
    path('all/', views.all_signals_view, name='all_signals'),
    path('<int:pk>/admin-delete/', views.admin_delete_signal, name='admin_delete_signal'),
]
