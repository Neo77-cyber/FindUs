from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, CraftsmanProfile, CustomerProfile, Service, Review

class BaseUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class CustomerSignUpForm(BaseUserForm):
    address = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False)
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (___) ___-____',
            'pattern': '^\+?\d{0,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}$',
            'title': 'Enter a valid phone number (e.g. +1 234 567 8900)'
        }),
        help_text="Format: +[country code][number]"
    )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        
        user_profile = UserProfile.objects.create(
            user=user,
            user_type='customer',
            
        )
        
        CustomerProfile.objects.create(
            user_profile=user_profile,
            address=self.cleaned_data.get('address'),
            city=self.cleaned_data.get('city'),
            state=self.cleaned_data.get('state'),
            country=self.cleaned_data.get('country'),
            postal_code=self.cleaned_data.get('postal_code')
        )
        return user
    
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['address', 'city', 'state', 'country', 'postal_code', 'phone']
        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your complete address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your state/province'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your country'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter postal/zip code'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number'
            }),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace(' ', '').replace('-', '').replace('+', '').isdigit():
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone

class CraftsmanSignUpForm(BaseUserForm):
    
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (___) ___-____',
            'pattern': '^\+?\d{0,3}[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}$',
            'title': 'Enter a valid phone number (e.g. +1 234 567 8900)'
        }),
        help_text="Format: +[country code][number]"
    )
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    country = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=100, required=True)
    postal_code = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    

    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        
        user_profile = UserProfile.objects.create(
            user=user,
            user_type='craftsman',
            
        )
        
        
        CraftsmanProfile.objects.create(
            user_profile=user_profile,
            phone=self.cleaned_data['phone'],
            address=self.cleaned_data['address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            postal_code=self.cleaned_data['postal_code'],
            country=self.cleaned_data['country'],
            
            
        )
        return user
    
class CraftsmanProfileForm(forms.ModelForm):
    class Meta:
        model = CraftsmanProfile
        fields = [
            'business_name',
            'service_category',
            'services_offered',
            'service_area',
            'phone',
            'years_of_experience',
            'profile_photo',
            'license_number',
            'description'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'services_offered': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'service_area': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['service_category'].widget.attrs.update({'class': 'form-control'})
        self.fields['years_of_experience'].widget.attrs.update({'class': 'form-control'})
        
        
        self.fields['service_category'].empty_label = 'Select Service'
        
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        
        return license_number
    

class ServiceForm(forms.ModelForm):
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Upload one service image"
    )
    
    
    AVAILABILITY_CHOICES = [
        ('immediate', 'Immediately Available'),
        ('24_hours', 'Within 24 Hours'),
        ('48_hours', 'Within 48 Hours'),
        ('scheduled', 'By Appointment Only'),
    ]
    
    SERVICE_SCOPE_CHOICES = [
        ('small', 'Small Job (1-2 hours)'),
        ('medium', 'Medium Job (Half day)'),
        ('large', 'Large Job (Full day+)'),
        ('project', 'Multi-day Project'),
    ]
    
    SERVICE_FEATURES = [
        ('emergency', '24/7 Emergency Service'),
        ('warranty', 'Service Warranty Included'),
        ('licensed', 'Fully Licensed'),
        ('insured', 'Insured & Bonded'),
        ('free_estimate', 'Free Estimate'),
        ('senior_discount', 'Senior Discount'),
    ]
    
    availability = forms.ChoiceField(
        choices=AVAILABILITY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='immediate'
    )
    
    job_size = forms.ChoiceField(
        choices=SERVICE_SCOPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    materials_included = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Materials included in price"
    )
    
    travel_fee = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 25.00'
        }),
        help_text="Additional travel fee"
    )
    
    features = forms.MultipleChoiceField(
        choices=SERVICE_FEATURES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    

    class Meta:
        model = Service
        fields = [
            'title',
            'category',
            'description',
            'price_type',
            'hourly_rate',
            'fixed_price',
            'estimated_duration',
            'min_hours',
            'image',
            'availability',
            'job_size',
            'materials_included',
            'travel_fee',
            'features',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Emergency Plumbing Repair'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your service in detail...'
            }),
            'price_type': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 50.00'
            }),
            'fixed_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 200.00'
            }),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2-3 hours'
            }),
            'min_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1 hour'
            }),
        }

    

    def clean(self):
        cleaned_data = super().clean()
        price_type = cleaned_data.get('price_type')
        hourly_rate = cleaned_data.get('hourly_rate')
        fixed_price = cleaned_data.get('fixed_price')
        
        
        if price_type == 'hourly' and not hourly_rate:
            raise forms.ValidationError("Hourly rate is required for hourly pricing")
        if price_type == 'fixed' and not fixed_price:
            raise forms.ValidationError("Fixed price is required for fixed pricing")
            
        return cleaned_data
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief summary of your experience'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share details of your experience with this service...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.choices = [
            (5, '⭐⭐⭐⭐⭐ Excellent'),
            (4, '⭐⭐⭐⭐ Very Good'),
            (3, '⭐⭐⭐ Good'),
            (2, '⭐⭐ Fair'),
            (1, '⭐ Poor'),
        ]
    