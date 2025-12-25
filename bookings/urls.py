from django.urls import path
from .views import (create_booking, booking_list, booking_detail,
                   update_booking_status, create_inquiry, inquiry_list,
                   update_inquiry_status)

urlpatterns = [
    path('create/<uuid:property_id>/', create_booking, name='create_booking'),
    path('', booking_list, name='booking_list'),
    path('<uuid:pk>/', booking_detail, name='booking_detail'),
    path('<uuid:pk>/status/<str:status>/', update_booking_status, name='update_booking_status'),
    path('inquiry/create/<uuid:property_id>/', create_inquiry, name='create_inquiry'),
    path('inquiries/', inquiry_list, name='inquiry_list'),
    path('inquiries/<uuid:pk>/status/<str:status>/', update_inquiry_status, name='update_inquiry_status'),
]