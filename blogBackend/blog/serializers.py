# blog/serializers.py
from rest_framework import serializers
from .models import BlogPost,Category, contact
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']  # Include fields you want to expose

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class BlogPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'short_description','categories', 'long_description', 'author', 'created_at', 'updated_at', 'published_at', 'is_published','main_image','thumbnail']
        
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = contact
        fields = '__all__'


