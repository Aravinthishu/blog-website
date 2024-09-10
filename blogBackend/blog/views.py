# blog/views.py
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BlogPost, contact
from .serializers import BlogPostSerializer,ContactSerializer
from rest_framework import generics
from .models import Category
from .serializers import CategorySerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view

class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class BlogPostsByCategory(generics.ListAPIView):
    serializer_class = BlogPostSerializer

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
        send_mail(subject, message, 'aravintharavinth6369@gmail.com', ['aravintharavinth6369@gmail.com'], fail_silently=False)

        return Response({'message': 'Form submitted successfully'})
    return Response(serializer.errors, status=400)