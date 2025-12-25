from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from properties.models import Property
import uuid

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landlord_bookings')
    
    # Booking details
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_occupants = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    security_deposit_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Student information
    student_message = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    landlord_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Dates
    booked_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Payment
    payment_status = models.CharField(max_length=20, default='pending')
    payment_id = models.CharField(max_length=255, blank=True)
    payment_receipt = models.FileField(upload_to='payment_receipts/', null=True, blank=True)
    
    class Meta:
        ordering = ['-booked_at']
    
    def __str__(self):
        return f"Booking {self.id} - {self.property.title}"
    
    @property
    def duration_months(self):
        from dateutil.relativedelta import relativedelta
        rd = relativedelta(self.check_out_date, self.check_in_date)
        return rd.years * 12 + rd.months

class Inquiry(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('responded', 'Responded'),
        ('closed', 'Closed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inquiry for {self.property.title} by {self.student.username}"