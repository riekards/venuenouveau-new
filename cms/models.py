from django.db import models

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    background_image = models.ImageField(upload_to='page_backgrounds/', blank=True, null=True)
    is_public = models.BooleanField(default=True)  # If False, page is hidden from public navigation
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class GalleryItem(models.Model):
    # This model is for the Gallery page (which you'll mark as not public)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='gallery_items')
    media_file = models.FileField(upload_to='gallery_media/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.page.title} - {self.caption}"
