# blog/serializers.py
from rest_framework import serializers
from .models import BlogPost,Category, Contact
from django.contrib.auth.models import User
from .models import BlogPost, Comment, Reply, CommentLike, CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()  # Or use CustomUserSerializer if needed
    categories = CategorySerializer(many=True, read_only=True)
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'short_description','categories', 'long_description', 'author', 'created_at', 'updated_at', 'published_at', 'is_published','main_image','thumbnail']
        
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


# ReplySerializer for replies on comments
class ReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Get the username or representation of the user

    class Meta:
        model = Reply  # Make sure the Reply model is correctly linked
        fields = ['id', 'comment', 'user', 'content', 'created_at', 'updated_at']  # Fields you want in the reply

# CommentSerializer that includes replies using the ReplySerializer
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Get the user as a string
    replies = ReplySerializer(many=True, read_only=True)  # Use ReplySerializer for nested replies
    likes = serializers.StringRelatedField(many=True, read_only=True)  # Assuming likes is related to user

    class Meta:
        model = Comment  # Link to Comment model
        fields = ['id', 'blog_post', 'user', 'content', 'created_at', 'updated_at', 'replies', 'likes']


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentLike
        fields = ['id', 'comment', 'user', 'liked_at']



from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match'})
        
        # Check if email is already used
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'This email is already used'})

        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user is None:
            raise serializers.ValidationError('Invalid email or password')
        return {'user': user}

class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email not found')
        return data

class SetNewPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        uidb64 = data.get('uidb64')
        token = data.get('token')
        password = data.get('password')

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError('Invalid token or user')

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError('Invalid token')

        return data