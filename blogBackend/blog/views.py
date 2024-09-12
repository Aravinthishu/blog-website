from rest_framework import viewsets, generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BlogPost, Category, Comment, Reply, CommentLike, Contact
from .serializers import BlogPostSerializer, ContactSerializer, CategorySerializer, CommentSerializer, ReplySerializer, CommentLikeSerializer, UserSerializer
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.contrib.auth import authenticate
from .models import CustomUser
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str



class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the profile of the currently authenticated user
        return self.request.user

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]  # Allow public access

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # Allow public access

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # Allow public access
    
class BlogPostsByCategory(generics.ListAPIView):
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]  # Allow public access

    def get_queryset(self):
        category_name = self.kwargs['category_name']
        return BlogPost.objects.filter(categories__name=category_name)

class BlogPostCreate(APIView):
    def post(self, request, format=None):
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def contact_form(request):
    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        subject = 'New Contact Form Submission'
        message = f'Name: {serializer.data["name"]}\n Email: {serializer.data["email"]}\nMessage: {serializer.data["message"]}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, ['aravintharavinth6369@gmail.com'], fail_silently=False)

        return Response({'message': 'Form submitted successfully'})
    return Response(serializer.errors, status=400)


class CommentListCreateAPI(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        """
        This method filters the comments based on the blog post ID provided in the query parameters.
        """
        blog_post_id = self.request.query_params.get('blog_post')  # Get the blog post ID from the query parameters
        if blog_post_id:
            return Comment.objects.filter(blog_post__id=blog_post_id)  # Filter comments by blog post ID
        return Comment.objects.none()  # Return no comments if blog_post is not provided

    def get_permissions(self):
        """
        Allow public access to view comments (GET), but require authentication for posting (POST).
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]  # Require authentication for POST (creating a comment)
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Public access to view replies, authentication only for POST
class ReplyListCreateAPI(generics.ListCreateAPIView):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]  # Require authentication only for POST (creating a reply)
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Authentication required only for liking comments
class LikeCommentAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

    def post(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        like, created = CommentLike.objects.get_or_create(comment=comment, user=request.user)
        if not created:  # If already liked, unlike it
            like.delete()
            liked = False
        else:
            liked = True
        return Response({'liked': liked, 'like_count': comment.likes.count()}, status=status.HTTP_200_OK)

# Authentication required only for deleting comments
class DeleteCommentAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Require authentication

    def delete(self, request, comment_id):
        comment = Comment.objects.get(id=comment_id, user=request.user)
        if comment:
            comment.is_active = False
            comment.save()
            return Response({'message': 'Comment deleted'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)


class RegisterAPI(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })

from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from .models import CustomUser

class ResetPasswordRequestAPI(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        uid = str(user.id)  # Convert user ID to string
        uidb64 = urlsafe_base64_encode(force_bytes(uid))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_link = f'http://localhost:3000/account/reset-password/{uidb64}/{token}/'
        print("uidb64: ",uidb64)
        print("token : ",token)

        send_mail(
            'Password Reset',
            f'Click the link to reset your password: {reset_link}',
            settings.EMAIL_HOST_USER,
            [email]
        )
        return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)

class SetNewPasswordAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uidb64 = serializer.validated_data['uidb64']
        token = serializer.validated_data['token']
        password = serializer.validated_data['password']

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({'error': 'Invalid token or user'}, status=status.HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)

