from django.urls import path
from . import views

urlpatterns = [

    path("", views.news_list_view, name="news"),

    path("create/", views.create_news, name="create_news"),

    path("api/map/news/", views.news_map_api, name="news-map"),
    path("edit/<int:news_id>/", views.edit_news, name="edit_news"),
    path("delete/<int:news_id>/", views.delete_news, name="delete_news"),

]