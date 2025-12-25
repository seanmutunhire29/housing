from django_jinja import library
from django.contrib.humanize.templatetags import humanize
from django.template.defaultfilters import date as date_filter
from django.utils import timezone

@library.filter
def naturaltime(value):
    return humanize.naturaltime(value)

@library.filter
def naturalday(value):
    return humanize.naturalday(value)

@library.filter
def intcomma(value):
    return humanize.intcomma(value)

@library.filter
def format_date(value, format_string='M d, Y'):
    if value:
        return date_filter(value, format_string)
    return ''

@library.filter
def time_ago(value):
    if not value:
        return ''
    now = timezone.now()
    diff = now - value
    
    if diff.days > 365:
        years = diff.days // 365
        return f'{years} year{"s" if years > 1 else ""} ago'
    elif diff.days > 30:
        months = diff.days // 30
        return f'{months} month{"s" if months > 1 else ""} ago'
    elif diff.days > 0:
        return f'{diff.days} day{"s" if diff.days > 1 else ""} ago'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    else:
        return 'just now'

@library.filter
def format_currency(value):
    try:
        return f'${float(value):,.2f}'
    except (ValueError, TypeError):
        return f'${0:,.2f}'

@library.filter
def stars(rating):
    """Generate star rating HTML"""
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    stars_html = ''
    stars_html += '<i class="fas fa-star text-yellow-400"></i> ' * full_stars
    if half_star:
        stars_html += '<i class="fas fa-star-half-alt text-yellow-400"></i> '
    stars_html += '<i class="far fa-star text-yellow-400"></i> ' * empty_stars
    return stars_html

@library.global_function
def get_user_type(user):
    if user.is_authenticated:
        return user.user_type
    return None

@library.global_function
def is_landlord(user):
    return user.is_authenticated and user.user_type == 'landlord'

@library.global_function
def is_student(user):
    return user.is_authenticated and user.user_type == 'student'

@library.global_function
def is_admin(user):
    return user.is_authenticated and user.is_staff