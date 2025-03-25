# cms/admin.py

from django.contrib import admin, messages
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Year, PricingPackage, PricingPackageVersion

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

    def has_add_permission(self, request, obj=None):
        # Disallow adding in the inline entirely
        return False

    def has_change_permission(self, request, obj=None):
        # Read-only
        return False


# Custom admin for PricingPackage.
class PricingPackageAdmin(admin.ModelAdmin):
    list_display = ('segment', 'year', 'package_name', 'current_version', 'approved')
    inlines = [PricingPackageVersionInline]
    readonly_fields = ('approved_by', 'approved_at')
    # Set a default change form template, but we will override it for the add view.
    # change_form_template = "cms/admin/pricingpackage/change_form.html"

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if object_id:
			# Use custom template for editing existing PricingPackages
            self.change_form_template = "cms/admin/pricingpackage/change_form.html"
        else:
            # Don't override the template at all — let Django use the default
            if hasattr(self, 'change_form_template'):
                del self.change_form_template
        return super().changeform_view(request, object_id, form_url, extra_context)

    
    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []  # no inlines on the add view
        return super().get_inline_instances(request, obj)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # URL for package-level approval (if needed).
            path('<path:object_id>/approve/', self.admin_site.admin_view(self.approve_view), name='cms_pricingpackage_approve'),
            # URL for approving a specific inline version.
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
            if change:
                if 'file' in form.changed_data:
                    obj.current_version += 1
                    obj.approved = False  # Reset approval on new file upload.
                    obj.approved_by = None
                    obj.approved_at = None
                    super().save_model(request, obj, form, change)

                    PricingPackageVersion.objects.create(
                        pricing_package=obj,
                        version=obj.current_version,
                        package_name=obj.package_name,
                        file=obj.file,
                        uploader=request.user.username,
                    )
                    return
            else:
                # New object: save first, then create version
                super().save_model(request, obj, form, change)

                PricingPackageVersion.objects.create(
                    pricing_package=obj,
                    version=obj.current_version,
                    package_name=obj.package_name,
                    file=obj.file,
                    uploader=request.user.username,
                )
        except Exception as e:
            # Optional: logs to console or error tracking system
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error in save_model: %s", e)
            raise  # re-raise so Django displays it


admin.site.register(PricingPackage, PricingPackageAdmin)
