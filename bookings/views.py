from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Booking, Inquiry
from .forms import BookingForm, InquiryForm
from accounts.decorators import student_required, landlord_required
from properties.models import Property
import datetime

@login_required
@student_required
def create_booking(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, is_active=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = request.user
            booking.property = property_obj
            booking.landlord = property_obj.landlord
            
            # Calculate total price
            months = booking.duration_months
            if months < 1:
                months = 1
            booking.total_price = property_obj.price_per_month * months
            
            booking.save()
            
            # Create notification for landlord
            from notifications.models import Notification
            Notification.objects.create(
                user=property_obj.landlord,
                notification_type='booking_request',
                title=f'New Booking Request',
                message=f'{request.user.get_full_name()} has requested to book your property: {property_obj.title}',
                data={'booking_id': str(booking.id), 'property_id': str(property_obj.id)}
            )
            
            messages.success(request, 'Booking request sent successfully!')
            return redirect('booking_detail', pk=booking.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BookingForm(initial={'property': property_obj})
    
    return render(request, 'bookings/create.jinja', {
        'form': form,
        'property': property_obj
    })

@login_required
def booking_list(request):
    if request.user.user_type == 'student':
        bookings = Booking.objects.filter(student=request.user).select_related('property', 'landlord')
    elif request.user.user_type == 'landlord':
        bookings = Booking.objects.filter(landlord=request.user).select_related('property', 'student')
    else:
        bookings = Booking.objects.none()
    
    # Get statistics
    pending_count = bookings.filter(status='pending').count()
    approved_count = bookings.filter(status='approved').count()
    completed_count = bookings.filter(status='completed').count()
    
    context = {
        'bookings': bookings,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'completed_count': completed_count,
    }
    return render(request, 'bookings/list.jinja', context)

@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, id=pk)
    
    # Check permission
    if not (request.user == booking.student or 
            request.user == booking.landlord or 
            request.user.is_staff):
        messages.error(request, 'You do not have permission to view this booking.')
        return redirect('booking_list')
    
    context = {
        'booking': booking,
        'can_approve': request.user == booking.landlord and booking.status == 'pending',
        'can_cancel': (request.user == booking.student and booking.status in ['pending', 'approved']) or
                      (request.user == booking.landlord and booking.status == 'pending'),
        'can_complete': request.user == booking.landlord and booking.status == 'approved',
    }
    return render(request, 'bookings/detail.jinja', context)

@login_required
@landlord_required
def update_booking_status(request, pk, status):
    booking = get_object_or_404(Booking, id=pk, landlord=request.user)
    
    valid_statuses = ['approved', 'rejected', 'cancelled', 'completed']
    if status not in valid_statuses:
        messages.error(request, 'Invalid status update.')
        return redirect('booking_detail', pk=pk)
    
    if request.method == 'POST':
        booking.status = status
        
        # Set timestamp for status change
        if status == 'approved':
            booking.approved_at = datetime.datetime.now()
        elif status == 'cancelled':
            booking.cancelled_at = datetime.datetime.now()
        elif status == 'completed':
            booking.completed_at = datetime.datetime.now()
        
        booking.save()
        
        # Create notification for student
        from notifications.models import Notification
        Notification.objects.create(
            user=booking.student,
            notification_type=f'booking_{status}',
            title=f'Booking {status.capitalize()}',
            message=f'Your booking for {booking.property.title} has been {status}.',
            data={'booking_id': str(booking.id)}
        )
        
        messages.success(request, f'Booking has been {status}.')
    
    return redirect('booking_detail', pk=pk)

@login_required
@student_required
def create_inquiry(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, is_active=True)
    
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.student = request.user
            inquiry.property = property_obj
            inquiry.save()
            
            # Create notification for landlord
            from notifications.models import Notification
            Notification.objects.create(
                user=property_obj.landlord,
                notification_type='inquiry',
                title='New Property Inquiry',
                message=f'{request.user.get_full_name()} has inquired about your property: {property_obj.title}',
                data={'inquiry_id': str(inquiry.id), 'property_id': str(property_obj.id)}
            )
            
            messages.success(request, 'Inquiry sent successfully!')
            return redirect('property_detail', pk=property_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InquiryForm()
    
    return render(request, 'bookings/create_inquiry.jinja', {
        'form': form,
        'property': property_obj
    })

@login_required
def inquiry_list(request):
    if request.user.user_type == 'student':
        inquiries = Inquiry.objects.filter(student=request.user).select_related('property')
    elif request.user.user_type == 'landlord':
        inquiries = Inquiry.objects.filter(property__landlord=request.user).select_related('property', 'student')
    else:
        inquiries = Inquiry.objects.none()
    
    # Get statistics
    new_count = inquiries.filter(status='new').count()
    responded_count = inquiries.filter(status='responded').count()
    
    context = {
        'inquiries': inquiries,
        'new_count': new_count,
        'responded_count': responded_count,
    }
    return render(request, 'bookings/inquiry_list.jinja', context)

@login_required
def update_inquiry_status(request, pk, status):
    inquiry = get_object_or_404(Inquiry, id=pk)
    
    # Check permission
    if not (request.user == inquiry.property.landlord or request.user.is_staff):
        messages.error(request, 'You do not have permission to update this inquiry.')
        return redirect('inquiry_list')
    
    valid_statuses = ['contacted', 'responded', 'closed']
    if status not in valid_statuses:
        messages.error(request, 'Invalid status update.')
        return redirect('inquiry_detail', pk=pk)
    
    if request.method == 'POST':
        inquiry.status = status
        inquiry.save()
        
        # Create notification for student if status changed to responded
        if status == 'responded':
            from notifications.models import Notification
            Notification.objects.create(
                user=inquiry.student,
                notification_type='inquiry_response',
                title='Inquiry Response',
                message=f'The landlord has responded to your inquiry about {inquiry.property.title}.',
                data={'inquiry_id': str(inquiry.id)}
            )
        
        messages.success(request, f'Inquiry status updated to {status}.')
    
    return redirect('inquiry_detail', pk=pk)