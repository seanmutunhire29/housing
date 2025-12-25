from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, StudentProfile, LandlordProfile
from django.core.validators import EmailValidator, RegexValidator

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        validators=[EmailValidator()]
    )
    phone_number = forms.CharField(
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.RadioSelect
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone_number', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Choose a username'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Your email address'})
        self.fields['phone_number'].widget.attrs.update({'placeholder': '+1234567890'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
            
            # Create profile based on user type
            if user.user_type == 'student':
                StudentProfile.objects.create(user=user)
            elif user.user_type == 'landlord':
                LandlordProfile.objects.create(user=user)
        
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username or Email'

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                 'profile_picture', 'university']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['budget_min', 'budget_max', 'preferred_location', 
                 'room_type_preference', 'move_in_date', 'special_requirements']
        widgets = {
            'move_in_date': forms.DateInput(attrs={'type': 'date'}),
            'special_requirements': forms.Textarea(attrs={'rows': 4}),
        }

class LandlordProfileForm(forms.ModelForm):
    class Meta:
        model = LandlordProfile
        fields = ['company_name', 'contact_person', 'address', 'tax_id']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'})
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Your old password was entered incorrectly.")
        return old_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', "The two password fields didn't match.")
        
        return cleaned_data
    
    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user