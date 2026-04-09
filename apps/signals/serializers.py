from rest_framework import serializers
from .models import Signal, SignalImage, Comment, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class SignalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalImage
        fields = ('id', 'image', 'uploaded_at')


class CommentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user_email', 'content', 'created_at')


class SignalListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Signal
        fields = (
            'id',
            'title',
            'category',
            'status',
            'status_display',
            'latitude',
            'longitude',
            'created_at',
        )


class SignalDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = SignalImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Signal
        fields = (
            'id',
            'title',
            'description',
            'category',
            'status',
            'status_display',
            'latitude',
            'longitude',
            'address',
            'user_email',
            'created_at',
            'updated_at',
            'images',
            'comments',
        )


class SignalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signal
        fields = (
            'title',
            'description',
            'category',
            'latitude',
            'longitude',
            'address',
        )
