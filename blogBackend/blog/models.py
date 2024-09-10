from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
from tinymce.models import HTMLField  # Or use your chosen rich text field

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class BlogPost(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.CharField(max_length=255)
    long_description = HTMLField()  # Using TinyMCE's HTMLField (or RichTextField, QuillField, etc.)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    main_image = models.ImageField(upload_to='blog_images/', null=True, blank=True)  # Main image field
    thumbnail = models.ImageField(upload_to='blog_thumbnails/', null=True, blank=True)  # Thumbnail image field
    categories = models.ManyToManyField(Category, related_name='blog_posts')  # Adding many-to-many field for categories
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class contact (models.Model):
    name = models.CharField(max_length=40)
    email = models.EmailField()
    message = models.TextField()
    
    def __str__(self):
        return self.name