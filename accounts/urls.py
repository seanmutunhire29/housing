from django.urls import path
from .views import (RegisterView, login_view, logout_view, dashboard,
                   profile, update_profile, change_password, PublicProfileView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('profile/update/', update_profile, name='update_profile'),
    path('profile/change-password/', change_password, name='change_password'),
    path('profile/<str:username>/', PublicProfileView.as_view(), name='public_profile'),
]