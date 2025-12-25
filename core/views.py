from django.shortcuts import render
from django.views.generic import TemplateView
from properties.models import Property
from django.db.models import Count, Avg, Q
import random

class HomeView(TemplateView):
    template_name = 'core/home.jinja'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured properties
        featured_properties = Property.objects.filter(
            is_active=True,
            is_verified=True
        ).select_related('landlord')[:8]
        
        # Get statistics
        total_properties = Property.objects.filter(is_active=True).count()
        verified_properties = Property.objects.filter(is_active=True, is_verified=True).count()
        active_landlords = Property.objects.filter(is_active=True).values('landlord').distinct().count()
        
        context.update({
            'featured_properties': featured_properties,
            'total_properties': total_properties,
            'verified_properties': verified_properties,
            'active_landlords': active_landlords,
        })
        return context

class AboutView(TemplateView):
    template_name = 'core/about.jinja'

class ContactView(TemplateView):
    template_name = 'core/contact.jinja'

class TermsView(TemplateView):
    template_name = 'core/terms.jinja'

class PrivacyView(TemplateView):
    template_name = 'core/privacy.jinja'

def handler404(request, exception):
    return render(request, 'core/404.jinja', status=404)

def handler500(request):
    return render(request, 'core/500.jinja', status=500)