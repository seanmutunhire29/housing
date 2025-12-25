from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from .forms import (UserRegistrationForm, UserLoginForm, UserUpdateForm,
                   StudentProfileForm, LandlordProfileForm, PasswordChangeForm)
from .models import User, StudentProfile, LandlordProfile
from .decorators import unauthenticated_user, student_required, landlord_required

class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.jinja'
    success_url = '/accounts/login/'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are already logged in.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please login.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on user type
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.jinja', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def dashboard(request):
    context = {}
    
    if request.user.user_type == 'student':
        # Student dashboard
        from properties.models import FavoriteProperty
        from bookings.models import Booking, Inquiry
        
        favorite_count = FavoriteProperty.objects.filter(user=request.user).count()
        booking_count = Booking.objects.filter(student=request.user).count()
        inquiry_count = Inquiry.objects.filter(student=request.user).count()
        
        context.update({
            'favorite_count': favorite_count,
            'booking_count': booking_count,
            'inquiry_count': inquiry_count,
            'recent_bookings': Booking.objects.filter(student=request.user).order_by('-created_at')[:5],
        })
    
    elif request.user.user_type == 'landlord':
        # Landlord dashboard
        from properties.models import Property
        from bookings.models import Booking, Inquiry
        
        property_count = Property.objects.filter(landlord=request.user).count()
        booking_count = Booking.objects.filter(landlord=request.user).count()
        inquiry_count = Inquiry.objects.filter(property__landlord=request.user).count()
        
        context.update({
            'property_count': property_count,
            'booking_count': booking_count,
            'inquiry_count': inquiry_count,
            'recent_inquiries': Inquiry.objects.filter(
                property__landlord=request.user
            ).order_by('-created_at')[:5],
            'recent_properties': Property.objects.filter(
                landlord=request.user
            ).order_by('-created_at')[:5],
        })
    
    elif request.user.is_staff:
        # Admin dashboard
        from properties.models import Property
        from bookings.models import Booking
        from accounts.models import User
        
        total_users = User.objects.count()
        total_properties = Property.objects.count()
        total_bookings = Booking.objects.count()
        pending_verifications = Property.objects.filter(is_verified=False).count()
        
        context.update({
            'total_users': total_users,
            'total_properties': total_properties,
            'total_bookings': total_bookings,
            'pending_verifications': pending_verifications,
        })
    
    return render(request, 'accounts/dashboard.jinja', context)

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
    
    context = {'user_form': user_form}
    
    # Add appropriate profile form
    if request.user.user_type == 'student' and hasattr(request.user, 'student_profile'):
        context['profile_form'] = StudentProfileForm(instance=request.user.student_profile)
    elif request.user.user_type == 'landlord' and hasattr(request.user, 'landlord_profile'):
        context['profile_form'] = LandlordProfileForm(instance=request.user.landlord_profile)
    
    return render(request, 'accounts/profile.jinja', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        if request.user.user_type == 'student' and hasattr(request.user, 'student_profile'):
            profile_form = StudentProfileForm(request.POST, instance=request.user.student_profile)
        elif request.user.user_type == 'landlord' and hasattr(request.user, 'landlord_profile'):
            profile_form = LandlordProfileForm(request.POST, instance=request.user.landlord_profile)
        else:
            messages.error(request, 'Profile not found.')
            return redirect('profile')
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile details have been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
            return redirect('profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.jinja', {'form': form})

class PublicProfileView(TemplateView):
    template_name = 'accounts/public_profile.jinja'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=kwargs['username'])
        context['profile_user'] = user
        
        if user.user_type == 'landlord' and hasattr(user, 'landlord_profile'):
            from properties.models import Property
            from reviews.models import Review
            
            context['landlord_profile'] = user.landlord_profile
            context['properties'] = Property.objects.filter(
                landlord=user,
                is_active=True,
                is_verified=True
            )[:6]
            context['reviews'] = Review.objects.filter(
                reviewed_user=user,
                is_approved=True
            )[:5]
        
        return context