from django.contrib import admin
from .models import Category, Signal
from .models import SignalImage
from .models import Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Signal)
class SignalAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'status',
        'user',
        'created_at',
    )
    list_filter = ('status', 'category')
    search_fields = ('title', 'description', 'address')

@admin.register(SignalImage)
class SignalImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'signal', 'uploaded_at')
    list_filter = ('uploaded_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'signal', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)