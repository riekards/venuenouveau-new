from django.contrib import admin, messages
from django.urls import path
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Year, PricingPackage, PricingPackageVersion, Page, GalleryItem
from django.db import transaction

class PageAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'is_public', 'last_updated')
	readonly_fields = ('slug', 'last_updated')

	def has_delete_permission(self, request, obj=None):
		return False

admin.site.register(Page, PageAdmin)
admin.site.register(GalleryItem)

# Register the Year model so that users can manage available years.
admin.site.register(Year)

# Inline for PricingPackageVersion: all fields are read-only and no manual adding/deleting.
class PricingPackageVersionInline(admin.TabularInline):
    model = PricingPackageVersion
    extra = 0
    readonly_fields = (
        'version',
        'package_name',
        'file',
        'uploader',
        'uploaded_at',
        'approved',
        'approved_by',
        'approved_at',
    )
    can_delete = False
    # Use our custom inline template to display an Approve button for unapproved versions.
    template = "cms/admin/pricingpackageversion/tabular.html"
    
    def has_add_permission(self, request, obj):
        return False

# Custom admin for PricingPackage.
class PricingPackageAdmin(admin.ModelAdmin):
    list_display = ('segment', 'year', 'package_name', 'current_version', 'approved')
    inlines = [PricingPackageVersionInline]
    readonly_fields = ('approved_by', 'approved_at')  # Keep only optional fields as readonly
    fields = ('segment', 'year', 'package_name', 'file', 'current_version', 'approved')  # Ensure required fields are included
    # Remove the custom change form template temporarily
    # change_form_template = "cms/admin/pricingpackage/change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Existing package-level approval (if you want a top-level Approve button)
            path('<path:object_id>/approve/', self.admin_site.admin_view(self.approve_view), name='cms_pricingpackage_approve'),
            # New URL for approving a specific inline version.
            path('<int:package_id>/approve_version/<int:version_id>/', 
                 self.admin_site.admin_view(self.approve_version_view),
                 name='cms_pricingpackage_approve_version'),
        ]
        return custom_urls + urls

    def approve_view(self, request, object_id, *args, **kwargs):
        obj = self.get_object(request, object_id)
        if not obj:
            self.message_user(request, "Object not found.", level=messages.ERROR)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))
        obj.approved = True
        obj.approved_by = request.user.username
        obj.approved_at = timezone.now()
        obj.save()
        # Also update the current version record.
        obj.versions.filter(version=obj.current_version).update(
            approved=True,
            approved_by=request.user.username,
            approved_at=timezone.now()
        )
        self.message_user(request, "Pricing package approved successfully.", level=messages.SUCCESS)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    def approve_version_view(self, request, package_id, version_id, *args, **kwargs):
        version = get_object_or_404(PricingPackageVersion, id=version_id, pricing_package_id=package_id)
        version.approved = True
        version.approved_by = request.user.username
        version.approved_at = timezone.now()
        version.save()
        self.message_user(request, "Pricing package version approved successfully.", level=messages.SUCCESS)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    def save_model(self, request, obj, form, change):
        try:
            print(f"Form data during save_model: {form.cleaned_data}")
            print(f"Object before saving: {obj.__dict__}")
            with transaction.atomic():  # Ensure the save is atomic
                super().save_model(request, obj, form, change)
            print(f"Object after saving: {obj.__dict__}")
            # Verify if the object exists in the database
            saved_obj = PricingPackage.objects.get(pk=obj.pk)
            print(f"Saved object from database: {saved_obj.__dict__}")
            # Add a success message
            self.message_user(request, "Pricing package saved successfully.", level=messages.SUCCESS)
        except Exception as e:
            print(f"Error saving PricingPackage: {e}")
            self.message_user(request, f"Error: {e}", level=messages.ERROR)
            raise

    def save_form(self, request, form, change):
        try:
            print(f"Form data before saving: {form.cleaned_data}")
            return super().save_form(request, form, change)
        except Exception as e:
            print(f"Error in form validation: {e}")
            raise

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        form_field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if form_field is not None:
            print(f"Field: {db_field.name}, Value: {form_field.initial}")
        else:
            print(f"Field: {db_field.name} has no form field.")
        return form_field

admin.site.register(PricingPackage, PricingPackageAdmin)