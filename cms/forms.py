from django import forms
from .models import PricingDocument

class PricingDocumentForm(forms.ModelForm):
    class Meta:
        model = PricingDocument
        # We'll allow selection of the PricingYear via the ForeignKey,
        # and file upload; version, approval, etc. are managed automatically.
        fields = ['year', 'file']
