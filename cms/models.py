# cms/models.py

from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class Page(models.Model):
    """
    Represents a single CMS-managed page with rich content.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    is_public = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if not set
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class GalleryItem(models.Model):
    """
    Media files attached to specific pages (e.g. images, videos).
    """
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='gallery_items')
    media_file = models.FileField(upload_to='gallery_media/')
    caption = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.page.title} - {self.caption}"


class Year(models.Model):
    """
    Represents the year associated with a pricing package (e.g. 2024).
    """
    year = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.year)


class PricingPackage(models.Model):
    """
    Main model for storing pricing packages per segment and year.
    Each save will track versions through the PricingPackageVersion model.
    """
    SEGMENT_CHOICES = [
        ('all_inclusive', 'All Inclusive Wedding Package'),
        ('venue_inclusive', 'Venue Inclusive Package'),
        ('weekday', 'Weekday Package'),
    ]

    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, null=True)
    package_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='packages/')
    current_version = models.PositiveIntegerField(default=1)
    approved = models.BooleanField(default=False)
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_segment_display()} - {self.year}"

    def clean(self):
        # Debug log (optional): ensure required fields are filled
        print("DEBUG CLEAN:")
        print(f"segment: {self.segment}")
        print(f"year: {self.year}")
        print(f"package_name: {self.package_name}")
        print(f"file: {self.file}")


class PricingPackageVersion(models.Model):
    """
    Stores version history of each PricingPackage.
    Automatically created when a new package is added or updated.
    """
    pricing_package = models.ForeignKey(PricingPackage, related_name='versions', on_delete=models.CASCADE)
    version = models.PositiveIntegerField()
    package_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='packages/versions/')
    uploader = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_by = models.CharField(max_length=100, blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Version {self.version} for {self.pricing_package}"
