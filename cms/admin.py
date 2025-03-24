from django.contrib import admin
from .models import Page, GalleryItem

class PageAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'is_public', 'last_updated')
	readonly_fields = ('slug', 'last_updated')

	def has_delete_permission(self, request, obj=None):
		return False

admin.site.register(Page, PageAdmin)
admin.site.register(GalleryItem)
