from django.db import models
from django.utils.text import slugify

class Page(models.Model):
	title = models.CharField(max_length=255)
	slug = models.SlugField(unique=True, blank=True)
	content = models.TextField()
	is_public = models.BooleanField(default=True)
	last_updated = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)
		super().save(*args, **kwargs)

	def __str__(self):
		return self.title


class GalleryItem(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='gallery_items')
    media_file = models.FileField(upload_to='gallery_media/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.page.title} - {self.caption}"
