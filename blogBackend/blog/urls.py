from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet
from .views import *

router = DefaultRouter()
router.register(r'blogposts', BlogPostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('create-blog/',BlogPostCreate.as_view(),name='create-blog'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<str:category_name>/', BlogPostsByCategory.as_view(), name='blogposts-by-category'),
    path('contact/', contact_form, name='contact_form'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
