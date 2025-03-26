# cms/admin.py

from django.contrib import admin, messages
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Year, PricingPackage, PricingPackageVersion

# Register Year for editing in admin
admin.site.register(Year)


class PricingPackageVersionInline(admin.TabularInline):
    """
    Read-only inline showing version history of a pricing package.
    """
    model = PricingPackageVersion
    extra = 0
    readonly_fields = (
        'version', 'package_name', 'file',
        'uploader', 'uploaded_at', 'approved',
        'approved_by', 'approved_at'
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        # Disable adding inlines manually
        return False

    def has_change_permission(self, request, obj=None):
        # Fully read-only inline
        return False


class PricingPackageAdmin(admin.ModelAdmin):
    list_display = ('segment', 'year', 'package_name', 'current_version', 'approved')
    inlines = [PricingPackageVersionInline]
    readonly_fields = ('approved_by', 'approved_at')

    def get_inline_instances(self, request, obj=None):
        # Only show inlines on the change view
        if obj is None:
            return []
        return super().get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        """
        Custom save logic:
        - If creating a new object, also create the first version
        - If updating and file changed, bump version and store new copy
        """
        try:
            if change:
                if 'file' in form.changed_data:
                    obj.current_version += 1
                    obj.approved = False
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
                # Save initial package
                super().save_model(request, obj, form, change)
                # Create version 1
                PricingPackageVersion.objects.create(
                    pricing_package=obj,
                    version=obj.current_version,
                    package_name=obj.package_name,
                    file=obj.file,
                    uploader=request.user.username,
                )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.exception("Error saving PricingPackage:")
            raise

    def get_urls(self):
        """
        Adds custom admin URLs for approval actions.
        """
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/approve/', self.admin_site.admin_view(self.approve_view),
                 name='cms_pricingpackage_approve'),
            path('<int:package_id>/approve_version/<int:version_id>/',
                 self.admin_site.admin_view(self.approve_version_view),
                 name='cms_pricingpackage_approve_version'),
        ]
        return custom_urls + urls

    def approve_view(self, request, object_id, *args, **kwargs):
        """
        Approves the main PricingPackage and its current version.
        """
        obj = self.get_object(request, object_id)
        if not obj:
            self.message_user(request, "Object not found.", level=messages.ERROR)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

        obj.approved = True
        obj.approved_by = request.user.username
        obj.approved_at = timezone.now()
        obj.save()

        obj.versions.filter(version=obj.current_version).update(
            approved=True,
            approved_by=request.user.username,
            approved_at=timezone.now()
        )

        self.message_user(request, "Pricing package approved successfully.", level=messages.SUCCESS)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))

    def approve_version_view(self, request, package_id, version_id, *args, **kwargs):
        """
        Approves a specific version in the inline history.
        """
        version = get_object_or_404(PricingPackageVersion, id=version_id, pricing_package_id=package_id)

        version.approved = True
        version.approved_by = request.user.username
        version.approved_at = timezone.now()
        version.save()

        self.message_user(request, "Pricing package version approved successfully.", level=messages.SUCCESS)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))


admin.site.register(PricingPackage, PricingPackageAdmin)
