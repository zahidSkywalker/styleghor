from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import UserAddress

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form"""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'full_name', 'phone_number', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize field labels and help text
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        self.fields['email'].help_text = 'Required. Enter a valid email address.'
        self.fields['full_name'].help_text = 'Enter your full name as it appears on official documents.'
        self.fields['phone_number'].help_text = 'Enter your phone number with country code (e.g., +8801712345678).'
        
        # Make email required
        self.fields['email'].required = True
        
        # Customize widgets
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter email address'
        })
        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+8801712345678'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('A user with this phone number already exists.')
        return phone_number

class CustomUserChangeForm(UserChangeForm):
    """Custom user change form"""
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'full_name', 'phone_number', 'date_of_birth', 
            'gender', 'profile_picture', 'address', 'city', 'state', 
            'country', 'zip_code'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize widgets
        for field_name, field in self.fields.items():
            if field_name != 'profile_picture':
                field.widget.attrs.update({'class': 'form-control'})
        
        # Customize specific fields
        self.fields['date_of_birth'].widget.attrs.update({
            'type': 'date',
            'class': 'form-control'
        })
        self.fields['gender'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['country'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['profile_picture'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError('A user with this email already exists.')
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            existing_user = User.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise forms.ValidationError('A user with this phone number already exists.')
        return phone_number

class UserAddressForm(forms.ModelForm):
    """Form for user addresses"""
    
    class Meta:
        model = UserAddress
        fields = [
            'address_type', 'recipient_name', 'phone_number', 
            'address_line_1', 'address_line_2', 'city', 'state', 
            'country', 'zip_code', 'landmark', 'delivery_instructions'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize widgets
        for field_name, field in self.fields.items():
            if field_name == 'address_type':
                field.widget.attrs.update({'class': 'form-select'})
            elif field_name == 'delivery_instructions':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Any special delivery instructions...'
                })
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Customize specific fields
        self.fields['recipient_name'].widget.attrs.update({
            'placeholder': 'Enter recipient name'
        })
        self.fields['phone_number'].widget.attrs.update({
            'placeholder': '+8801712345678'
        })
        self.fields['address_line_1'].widget.attrs.update({
            'placeholder': 'House/Flat No., Street Address'
        })
        self.fields['address_line_2'].widget.attrs.update({
            'placeholder': 'Apartment, suite, etc. (optional)'
        })
        self.fields['city'].widget.attrs.update({
            'placeholder': 'Enter city name'
        })
        self.fields['state'].widget.attrs.update({
            'placeholder': 'Enter state/province'
        })
        self.fields['zip_code'].widget.attrs.update({
            'placeholder': 'Enter zip/postal code'
        })
        self.fields['landmark'].widget.attrs.update({
            'placeholder': 'Nearby landmark (optional)'
        })
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Basic phone number validation
            import re
            phone_pattern = r'^\+?1?\d{9,15}$'
            if not re.match(phone_pattern, phone_number):
                raise forms.ValidationError('Please enter a valid phone number.')
        return phone_number
    
    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        if zip_code:
            # Basic zip code validation
            import re
            zip_pattern = r'^\d{4,10}$'
            if not re.match(zip_pattern, zip_code):
                raise forms.ValidationError('Please enter a valid zip/postal code.')
        return zip_code

class PasswordChangeForm(forms.Form):
    """Form for changing password"""
    
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password'
        })
    )
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        help_text='Password must be at least 8 characters long and contain letters and numbers.'
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        
        # Check if password contains both letters and numbers
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            raise forms.ValidationError('Password must contain both letters and numbers.')
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('New passwords do not match.')
        
        return cleaned_data

class ForgotPasswordForm(forms.Form):
    """Form for forgot password"""
    
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        }),
        help_text='Enter the email address associated with your account.'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                raise forms.ValidationError('No account found with this email address.')
        return email

class AccountSettingsForm(forms.Form):
    """Form for account settings"""
    
    newsletter_subscribed = forms.BooleanField(
        label='Subscribe to Newsletter',
        required=False,
        help_text='Receive updates about new products, sales, and fashion trends.'
    )
    
    marketing_emails = forms.BooleanField(
        label='Marketing Emails',
        required=False,
        help_text='Receive promotional emails and special offers.'
    )
    
    sms_notifications = forms.BooleanField(
        label='SMS Notifications',
        required=False,
        help_text='Receive order updates and delivery notifications via SMS.'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Set initial values from user preferences
            self.fields['newsletter_subscribed'].initial = user.is_newsletter_subscribed
            self.fields['marketing_emails'].initial = user.marketing_emails
            self.fields['sms_notifications'].initial = user.sms_notifications

class DeleteAccountForm(forms.Form):
    """Form for account deletion confirmation"""
    
    password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to confirm'
        }),
        help_text='This action cannot be undone. All your data will be permanently deleted.'
    )
    
    confirm_delete = forms.BooleanField(
        label='I understand that this action cannot be undone',
        required=True,
        help_text='Check this box to confirm that you want to delete your account.'
    )