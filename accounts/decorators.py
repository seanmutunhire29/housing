from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You are already logged in.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper_func

def student_required(view_func):
    @login_required
    def wrapper_func(request, *args, **kwargs):
        if request.user.user_type == 'student' or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
    return wrapper_func

def landlord_required(view_func):
    @login_required
    def wrapper_func(request, *args, **kwargs):
        if request.user.user_type == 'landlord' or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
    return wrapper_func

def admin_required(view_func):
    @login_required
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
    return wrapper_func