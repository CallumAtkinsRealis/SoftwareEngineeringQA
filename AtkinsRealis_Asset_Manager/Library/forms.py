from django import forms
from .models import CustomUser, AssetBooking
from django.contrib.auth import get_user_model

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname', 'job_title', 'is_active', 'is_staff']  # Add other fields as needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form field labels if needed
        self.fields['firstname'].label = 'First Name'
        self.fields['lastname'].label = 'Last Name'
        self.fields['job_title'].label = 'Job Title'
        self.fields['is_active'].label = 'Active'
        self.fields['is_staff'].label = 'Staff'

    def clean(self):
        cleaned_data = super().clean()
        # Add custom validation logic if needed
        return cleaned_data
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    
class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'firstname', 'lastname', 'job_title', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    
class AssetBookingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AssetBookingForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AssetBooking
        fields = ['booked_by', 'asset_category', 'asset_name', 'project_name', 'project_number', 'project_manager', 'date_booked_for', 'date_to', 'duration', 'approved']
        widgets = {
            'date_booked_for': forms.DateInput(attrs={'class': 'form-control', 'id': 'datepicker'}),
            'date_to': forms.TextInput(attrs={'class': 'form-control', 'id': 'date_to'}),  # Changed to TextInput
        }