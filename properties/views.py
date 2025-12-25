from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Property, PropertyImage, FavoriteProperty, Amenity
from .forms import PropertyForm, PropertySearchForm
from accounts.decorators import landlord_required

class PropertyListView(ListView):
    model = Property
    template_name = 'properties/list.jinja'
    context_object_name = 'properties'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True).select_related('landlord')
        
        # Apply filters from form
        form = PropertySearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            city = form.cleaned_data.get('city')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            property_type = form.cleaned_data.get('property_type')
            room_type = form.cleaned_data.get('room_type')
            bedrooms = form.cleaned_data.get('bedrooms')
            furnished = form.cleaned_data.get('furnished')
            pet_friendly = form.cleaned_data.get('pet_friendly')
            utilities_included = form.cleaned_data.get('utilities_included')
            has_parking = form.cleaned_data.get('has_parking')
            
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(address__icontains=query) |
                    Q(city__icontains=query) |
                    Q(nearest_university__icontains=query)
                )
            if city:
                queryset = queryset.filter(city__icontains=city)
            if min_price:
                queryset = queryset.filter(price_per_month__gte=min_price)
            if max_price:
                queryset = queryset.filter(price_per_month__lte=max_price)
            if property_type:
                queryset = queryset.filter(property_type=property_type)
            if room_type:
                queryset = queryset.filter(room_type=room_type)
            if bedrooms:
                queryset = queryset.filter(bedrooms=bedrooms)
            if furnished:
                queryset = queryset.filter(furnished=True)
            if pet_friendly:
                queryset = queryset.filter(pet_friendly=True)
            if utilities_included:
                queryset = queryset.filter(utilities_included=True)
            if has_parking:
                queryset = queryset.filter(has_parking=True)
        
        # Order by verified first, then by creation date
        queryset = queryset.order_by('-is_verified', '-created_at')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PropertySearchForm(self.request.GET)
        
        # Add statistics
        context['total_properties'] = Property.objects.filter(is_active=True).count()
        context['verified_properties'] = Property.objects.filter(is_active=True, is_verified=True).count()
        
        # Check favorites for authenticated users
        if self.request.user.is_authenticated:
            favorite_ids = FavoriteProperty.objects.filter(
                user=self.request.user
            ).values_list('property_id', flat=True)
            context['favorite_ids'] = list(favorite_ids)
        
        return context

class PropertyDetailView(DetailView):
    model = Property
    template_name = 'properties/detail.jinja'
    context_object_name = 'property'
    
    def get_queryset(self):
        return Property.objects.filter(is_active=True).select_related('landlord')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_obj = self.get_object()
        
        # Increment view count
        property_obj.view_count += 1
        property_obj.save(update_fields=['view_count'])
        
        # Get related properties
        related_properties = Property.objects.filter(
            is_active=True,
            is_verified=True,
            city=property_obj.city
        ).exclude(id=property_obj.id)[:4]
        
        # Check if property is in user's favorites
        is_favorite = False
        if self.request.user.is_authenticated:
            is_favorite = FavoriteProperty.objects.filter(
                user=self.request.user,
                property=property_obj
            ).exists()
        
        # Get reviews
        from reviews.models import Review
        reviews = Review.objects.filter(
            property=property_obj,
            is_approved=True
        ).select_related('reviewer')[:10]
        
        context.update({
            'is_favorite': is_favorite,
            'related_properties': related_properties,
            'reviews': reviews,
            'average_rating': reviews.aggregate(models.Avg('overall_rating'))['overall_rating__avg'],
        })
        return context

@login_required
@landlord_required
def create_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.landlord = request.user
            property_obj.save()
            
            # Save images
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image,
                    is_primary=(i == 0)
                )
            
            # Save amenities
            amenities_text = form.cleaned_data.get('amenities', '')
            if amenities_text:
                amenities = [a.strip() for a in amenities_text.split(',') if a.strip()]
                for amenity in amenities:
                    Amenity.objects.create(
                        property=property_obj,
                        name=amenity
                    )
            
            messages.success(request, 'Property created successfully! It will be visible after verification.')
            return redirect('property_detail', pk=property_obj.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyForm()
    
    return render(request, 'properties/create.jinja', {'form': form})

@login_required
@landlord_required
def update_property(request, pk):
    property_obj = get_object_or_404(Property, id=pk, landlord=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            property_obj = form.save()
            
            # Handle new images
            images = request.FILES.getlist('images')
            if images:
                for i, image in enumerate(images):
                    PropertyImage.objects.create(
                        property=property_obj,
                        image=image,
                        is_primary=(i == 0 and not property_obj.images.filter(is_primary=True).exists())
                    )
            
            # Handle amenities
            amenities_text = form.cleaned_data.get('amenities', '')
            if amenities_text:
                # Clear existing amenities
                property_obj.amenities.all().delete()
                # Add new amenities
                amenities = [a.strip() for a in amenities_text.split(',') if a.strip()]
                for amenity in amenities:
                    Amenity.objects.create(
                        property=property_obj,
                        name=amenity
                    )
            
            messages.success(request, 'Property updated successfully!')
            return redirect('property_detail', pk=property_obj.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Prepare initial data
        initial = {}
        amenities = property_obj.amenities.all()
        if amenities.exists():
            initial['amenities'] = ', '.join([a.name for a in amenities])
        
        form = PropertyForm(instance=property_obj, initial=initial)
    
    return render(request, 'properties/update.jinja', {'form': form, 'property': property_obj})

@login_required
@landlord_required
def delete_property(request, pk):
    property_obj = get_object_or_404(Property, id=pk, landlord=request.user)
    
    if request.method == 'POST':
        property_obj.is_active = False
        property_obj.save()
        messages.success(request, 'Property deleted successfully!')
        return redirect('my_properties')
    
    return render(request, 'properties/delete.jinja', {'property': property_obj})

@login_required
def toggle_favorite(request, pk):
    property_obj = get_object_or_404(Property, id=pk, is_active=True)
    
    if request.method == 'POST':
        favorite, created = FavoriteProperty.objects.get_or_create(
            user=request.user,
            property=property_obj
        )
        
        if created:
            property_obj.favorite_count += 1
            property_obj.save()
            messages.success(request, 'Property added to favorites!')
        else:
            favorite.delete()
            property_obj.favorite_count -= 1
            property_obj.save()
            messages.success(request, 'Property removed from favorites!')
    
    return redirect(request.META.get('HTTP_REFERER', 'property_list'))

@login_required
def my_properties(request):
    properties = Property.objects.filter(landlord=request.user).order_by('-created_at')
    
    # Get statistics
    total_properties = properties.count()
    active_properties = properties.filter(is_active=True).count()
    verified_properties = properties.filter(is_verified=True).count()
    
    context = {
        'properties': properties,
        'total_properties': total_properties,
        'active_properties': active_properties,
        'verified_properties': verified_properties,
    }
    return render(request, 'properties/my_properties.jinja', context)

@login_required
def my_favorites(request):
    favorites = FavoriteProperty.objects.filter(user=request.user).select_related('property')
    properties = [fav.property for fav in favorites]
    
    context = {
        'properties': properties,
        'favorite_count': favorites.count(),
    }
    return render(request, 'properties/favorites.jinja', context)