from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from .models import AssetBooking, CustomUser

class AssetBookingForm(forms.ModelForm):
    #Form for Asset Booking
    def __init__(self, *args, **kwargs):
        super(AssetBookingForm, self).__init__(*args, **kwargs)

        # Modify booked_by field
        self.fields['booked_by'].empty_label = "---------"
        self.fields['booked_by'].required = False
        self.fields['booked_by'].queryset = CustomUser.objects.all()

        # Modify project_manager field
        self.fields['project_manager'].empty_label = "---------"
        self.fields['project_manager'].required = False
        self.fields['project_manager'].queryset = CustomUser.objects.all()

    class Meta:
        model = AssetBooking
        fields = ['booked_by', 'asset_category', 'asset_name', 'project_name', 'project_number', 'project_manager', 'date_booked_for', 'approved']
        widgets = {
            'date_booked_for': forms.DateInput(attrs={'class': 'form-control', 'id': 'datepicker'}),
            'date_to': forms.TextInput(attrs={'class': 'form-control', 'id': 'date_to'}),  # Changed to TextInput
        }

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'firstname', 'lastname', 'job_title', 'password', 'is_staff']

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

class CustomUserForm(forms.ModelForm):
    #Form for user update
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname', 'job_title', 'is_active', 'is_staff']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize form field labels if needed
        self.fields['firstname'].label = 'First Name'
        self.fields['lastname'].label = 'Last Name'
        self.fields['job_title'].label = 'Job Title'
        self.fields['is_active'].label = 'Active'
        self.fields['is_staff'].label = 'Staff'

    def save(self, commit=True):
        user = super().save(commit=False)
        # Hash the password if it's provided and not empty
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    #Log In form options
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
