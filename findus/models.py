from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('craftsman', 'Craftsman'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    
    def __str__(self):
        return self.user.username



class CraftsmanProfile(models.Model):

    SERVICE_CATEGORIES = [
    ('plumbing', 'Plumber'),
    ('electrical', 'Electrician'),
    ('ac_technician', 'AC Technician'),
    ('carpentry', 'Carpenter'),
    ('tiling', 'Tiler'),
    ('painting', 'Painter'),
    ('furniture_maker', 'Furniture Maker'),
    ('fumigation', 'Fumigator'),
    ('dstv_technician', 'DSTV Technician'),
    ('gas_appliance', 'Gas Appliance Technician'),
    ('pop_worker', 'POP Worker'),
    ('cleaning', 'Cleaner'),
    ('aluminium_worker', 'Aluminium Worker'),
    ('welding', 'Welder'),
    ('roofing', 'Roof Technician'),
    ('solar_power', 'Solar Power Technician'),
    ('masonry', 'Mason'),
    ('glass_partitioning', 'Glass/Partitioning Worker'),
    ('bricklayer', 'Bricklayer / Plasterer'),
    ('foreman', 'Foreman'),
    ('landscaping', 'Landscaping'),
    ('appliance_repair', 'Appliance Repair'),
    ('hvac', 'HVAC Services'),
    ('security_installation', 'CCTV / Security System Technician'),
    ('generator_technician', 'Generator Technician'),
    ('interior_design', 'Interior Designer'),
    ('flooring', 'Flooring / Epoxy Work'),
    ('metal_fabrication', 'Metal Fabrication'),
    ('waterproofing', 'Waterproofing Specialist'),
    ('pest_control', 'Pest Control'),
    ('scaffolding', 'Scaffolding Worker'),
    ('site_supervisor', 'Site Supervisor'),
    ('other', 'Other'),
]


    user_profile = models.OneToOneField('UserProfile', on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255)
    service_category = models.CharField(
        max_length=100,
        choices=SERVICE_CATEGORIES
    )
    services_offered = models.TextField()
    service_area = models.CharField(max_length=255)
    years_of_experience = models.CharField(max_length=20, choices=[
        ('0-1', '0-1 years'),
        ('1-3', '1-3 years'),
        ('3-5', '3-5 years'),
        ('5+', '5+ years'),
    ])
    profile_photo = models.ImageField(upload_to='craftsman_profiles/', null=True, blank=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    is_verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(
        max_length=20
    )
    

    def __str__(self):
        return f"{self.user_profile.user.get_full_name()} - {self.business_name}"

    def has_complete_profile(self):
        
        required_fields = [
            self.business_name,
            self.service_category,
            self.services_offered,
            self.service_area,
            self.phone,
            self.description,
            self.address,
            self.city,
            self.state,
            self.country,
            self.postal_code
        ]
        return all(required_fields)

class CustomerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(
        max_length=20, blank=True, null=True
    )
    
    def __str__(self):
        return self.user_profile.user.get_full_name()
    


class Service(models.Model):
    CATEGORY_CHOICES = [
        ('plumbing', 'Plumber'),
    ('electrical', 'Electrician'),
    ('ac_technician', 'AC Technician'),
    ('carpentry', 'Carpenter'),
    ('tiling', 'Tiler'),
    ('painting', 'Painter'),
    ('furniture_maker', 'Furniture Maker'),
    ('fumigation', 'Fumigator'),
    ('dstv_technician', 'DSTV Technician'),
    ('gas_appliance', 'Gas Appliance Technician'),
    ('pop_worker', 'POP Worker'),
    ('cleaning', 'Cleaner'),
    ('aluminium_worker', 'Aluminium Worker'),
    ('welding', 'Welder'),
    ('roofing', 'Roof Technician'),
    ('solar_power', 'Solar Power Technician'),
    ('masonry', 'Mason'),
    ('glass_partitioning', 'Glass/Partitioning Worker'),
    ('bricklayer', 'Bricklayer / Plasterer'),
    ('foreman', 'Foreman'),
    ('landscaping', 'Landscaping'),
    ('appliance_repair', 'Appliance Repair'),
    ('hvac', 'HVAC Services'),
    ('security_installation', 'CCTV / Security System Technician'),
    ('generator_technician', 'Generator Technician'),
    ('interior_design', 'Interior Designer'),
    ('flooring', 'Flooring / Epoxy Work'),
    ('metal_fabrication', 'Metal Fabrication'),
    ('waterproofing', 'Waterproofing Specialist'),
    ('pest_control', 'Pest Control'),
    ('scaffolding', 'Scaffolding Worker'),
    ('site_supervisor', 'Site Supervisor'),
    ('other', 'Other'),
    ]
    
    PRICE_TYPE_CHOICES = [
        ('hourly', 'Hourly Rate'),
        ('fixed', 'Fixed Price'),
    ]

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
    
    craftsman = models.ForeignKey('CraftsmanProfile', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE_CHOICES)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fixed_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    estimated_duration = models.CharField(max_length=100)
    min_hours = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)
    availability = models.CharField(
        max_length=20,
        choices=AVAILABILITY_CHOICES,
        default='immediate'
    )
    job_size = models.CharField(
        max_length=20,
        choices=SERVICE_SCOPE_CHOICES,
        default='medium'
    )
    materials_included = models.BooleanField(default=False)
    travel_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    features = models.JSONField(default=list, blank=True)
    service_status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.get_category_display()}"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['service', 'customer']  
    
    def __str__(self):
        return f"{self.customer.user_profile.user.get_full_name()} - {self.service.title} - {self.rating} stars"

class SavedService(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='saved_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'service']  
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.user_profile.user.get_full_name()} saved {self.service.title}"