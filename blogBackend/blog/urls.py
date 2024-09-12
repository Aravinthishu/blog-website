from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'blogposts', BlogPostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<str:category_name>/', BlogPostsByCategory.as_view(), name='blogposts-by-category'),
    path('contact/', contact_form, name='contact_form'),
    path('comments/', CommentListCreateAPI.as_view(), name='comment-list-create'),
    path('replies/', ReplyListCreateAPI.as_view(), name='reply-list-create'),
    path('comments/<int:comment_id>/like/', LikeCommentAPI.as_view(), name='like-comment'),
    path('comments/<int:comment_id>/delete/', DeleteCommentAPI.as_view(), name='delete-comment'),
    
    path('register/', RegisterAPI.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Password Reset
    path('password-reset/', ResetPasswordRequestAPI.as_view(), name='password_reset'),
    path('password-reset/confirm/', SetNewPasswordAPI.as_view(), name='password_reset_confirm'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
]
