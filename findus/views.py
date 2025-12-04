from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from .forms import *
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Case, When, F, Value, DecimalField, Avg, Count
import decimal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.http import JsonResponse



logger = logging.getLogger(__name__)





def home(request):
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            print("User logged in, redirecting...")
            return redirect('signin')
        else:
            
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomerSignUpForm()
    
    return render(request, 'home.html', {'form': form})

def register_craftsman(request):
    if request.method == 'POST':
        form = CraftsmanSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('signin')  
    else:
        form = CraftsmanSignUpForm()
    
    return render(request, 'register_craftsman.html', {'form': form})




def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password') 
        user = authenticate(request, username=username, password=password)
        
        if user:    
            
            try:
                user.userprofile.craftsmanprofile
                login(request, user)
                return redirect('craftsman_dashboard')
            except CraftsmanProfile.DoesNotExist:
                pass
                
            
            try:
                user.userprofile.customerprofile
                login(request, user)
                return redirect('customer_dashboard')
            except CustomerProfile.DoesNotExist:
                pass
                
            messages.error(request, 'Account type not recognized')
        else:
            messages.error(request, 'Wrong username or password')
    
    return render(request, 'signin.html')



def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()

            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {'form': form})



@login_required
def customer_dashboard(request):

    if not request.GET and 'user_state' in request.session:
        request.session.pop('user_state', None)
        request.session.pop('user_city', None)
        print("🗑️ Location cleared via Clear Filters")

    auto_detect = request.GET.get('auto_detect')
    location_param = request.GET.get('location')
    
    # Get services with calculated ratings and review counts
    services = Service.objects.select_related(
        'craftsman',
        'craftsman__user_profile', 
        'craftsman__user_profile__user'
    ).annotate(
        avg_rating=Coalesce(
            Avg('reviews__rating'),
            Value(0.0),
            output_field=models.FloatField()
        ),
        review_count=Count('reviews', distinct=True)
    ).all()


    if auto_detect and location_param:
        print(f"🔍 AUTO_DETECT: Saving location from GET parameter: {location_param}")
        request.session['user_state'] = location_param
        request.session['user_city'] = 'Auto-detected'
    
    # === FILTERS ===
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        services = services.filter(category=category_filter)
    
    # Price type filter
    price_type_filter = request.GET.get('price_type', '')
    if price_type_filter:
        services = services.filter(price_type=price_type_filter)
    
    # Location filter
    location_filter = request.GET.get('location', '')
    if location_filter:
        services = services.filter(
            models.Q(craftsman__city__icontains=location_filter) |
            models.Q(craftsman__state__icontains=location_filter)
        )
    
    # Availability filter
    availability_filter = request.GET.get('availability', '')
    if availability_filter:
        services = services.filter(availability=availability_filter)
    
    # Job size filter
    job_size_filter = request.GET.get('job_size', '')
    if job_size_filter:
        services = services.filter(job_size=job_size_filter)
    
    # Price range filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price or max_price:
        services = services.annotate(
            effective_price=Case(
                When(price_type='hourly', then=F('hourly_rate')),
                When(price_type='fixed', then=F('fixed_price')),
                default=Value(0),
                output_field=DecimalField(),
            )
        )
        if min_price:
            services = services.filter(effective_price__gte=decimal.Decimal(min_price))
        if max_price:
            services = services.filter(effective_price__lte=decimal.Decimal(max_price))
    
    # Features filter
    features_filter = request.GET.getlist('features')
    if features_filter:
        services = services.filter(features__overlap=features_filter)
    
    # Materials included filter
    materials_included = request.GET.get('materials_included')
    if materials_included:
        services = services.filter(materials_included=True)
    
    # === SORTING ===
    sort_by = request.GET.get('sort', '')
    if sort_by == 'price_low_high':
        if not (min_price or max_price):  # Only annotate if not already done
            services = services.annotate(
                effective_price=Case(
                    When(price_type='hourly', then=F('hourly_rate')),
                    When(price_type='fixed', then=F('fixed_price')),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            )
        services = services.order_by('effective_price')
    elif sort_by == 'price_high_low':
        if not (min_price or max_price):
            services = services.annotate(
                effective_price=Case(
                    When(price_type='hourly', then=F('hourly_rate')),
                    When(price_type='fixed', then=F('fixed_price')),
                    default=Value(0),
                    output_field=DecimalField(),
                )
            )
        services = services.order_by('-effective_price')
    elif sort_by == 'rating':
        services = services.order_by('-avg_rating')  # Use the annotated avg_rating
    else:
        services = services.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(services, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Build preserved querystring
    preserved_params = request.GET.copy()
    if 'page' in preserved_params:
        preserved_params.pop('page')
    querystring = preserved_params.urlencode()
    
    context = {
        'page_obj': page_obj,
        'services': page_obj,
        'available_categories': Service.CATEGORY_CHOICES,
        'availability_choices': Service.AVAILABILITY_CHOICES,
        'job_size_choices': Service.SERVICE_SCOPE_CHOICES,
        'features_choices': ServiceForm.SERVICE_FEATURES,
        'selected_category': category_filter,
        'selected_price_type': price_type_filter,
        'selected_location': location_filter,
        'selected_availability': availability_filter,
        'selected_job_size': job_size_filter,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
        'selected_features': features_filter,
        'selected_materials_included': materials_included,
        'selected_sort': sort_by,
        'querystring': querystring,
        'user_state': request.session.get('user_state', ''),
    }
    
    return render(request, 'customer_dashboard.html', context)


def save_user_location(request):
    if request.method == 'POST':
        state = request.POST.get('state')
        city = request.POST.get('city')
        
        print(f"🔍 SAVE_LOCATION: Received state='{state}', city='{city}'")
        
        if state:
            request.session['user_state'] = state
            request.session['user_city'] = city
            print(f"💾 SAVE_LOCATION: Saved to session - user_state='{state}'")
            return JsonResponse({'success': True})
        else:
            # Clear location if state is empty
            request.session.pop('user_state', None)
            request.session.pop('user_city', None)
            print("🗑️ SAVE_LOCATION: Cleared location from session")
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
def service_detail(request, service_id):
    try:
        service = Service.objects.select_related(
            'craftsman',
            'craftsman__user_profile', 
            'craftsman__user_profile__user'
        ).annotate(
            avg_rating=Coalesce(
                Avg('reviews__rating'),
                Value(0.0),
                output_field=models.FloatField()
            ),
            review_count=Count('reviews', distinct=True)
        ).get(id=service_id)
        
        # Get related services with ratings
        related_services = Service.objects.filter(
            category=service.category,
            craftsman__is_verified=True
        ).exclude(id=service_id).annotate(
            avg_rating=Coalesce(
                Avg('reviews__rating'),
                Value(0.0),
                output_field=models.FloatField()
            ),
            review_count=Count('reviews', distinct=True)
        ).order_by('-created_at')[:4]
        
    except Service.DoesNotExist:
        messages.error(request, "Service not found.")
        return redirect('customer_dashboard')
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    
    return render(request, 'service_detail.html', context)

def get_rating_distribution(reviews):
    """Calculate rating distribution for the chart"""
    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    total = reviews.count()
    
    for review in reviews:
        distribution[review.rating] += 1
    
    # Convert to percentages
    if total > 0:
        for rating in distribution:
            distribution[rating] = (distribution[rating] / total) * 100
    
    return distribution


@login_required
def craftsman_dashboard(request):
    try:
        craftsman = request.user.userprofile.craftsmanprofile
    except Exception as e:
        messages.error(request, "You need to be a registered craftsman")
        return redirect('home')

    service_id = request.GET.get('edit')  
    delete_id = request.GET.get('delete')
    editing_service = None
    
    # Handle service deletion
    if delete_id:
        try:
            service_to_delete = Service.objects.get(id=delete_id, craftsman=craftsman)
            service_title = service_to_delete.title
            service_to_delete.delete()
            messages.success(request, f"Service '{service_title}' has been deleted successfully!")
            return redirect('craftsman_dashboard')
        except Service.DoesNotExist:
            messages.error(request, "Service not found")
            return redirect('craftsman_dashboard')
    
    # Handle service editing
    if service_id:
        try:
            editing_service = Service.objects.get(id=service_id, craftsman=craftsman)
        except Service.DoesNotExist:
            messages.error(request, "Service not found")
            return redirect('craftsman_dashboard')

    if request.method == 'POST':
        if editing_service:
            form = ServiceForm(request.POST, request.FILES, instance=editing_service)
            action = "updated"
        else:
            form = ServiceForm(request.POST, request.FILES)
            action = "created"
            
        if form.is_valid():
            try:
                service = form.save(commit=False)
                if not editing_service:
                    service.craftsman = craftsman
                    service.service_status = 'Active'
                
                service.save()
                form.save_m2m()  
                
                messages.success(request, f"Service {action} successfully!")
                return redirect('craftsman_dashboard')  
                
            except Exception as e:
                messages.error(request, f"Error saving service: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        if editing_service:
            form = ServiceForm(instance=editing_service)
        else:
            form = ServiceForm()

    # Get services with calculated ratings and review counts
    services_list = Service.objects.filter(craftsman=craftsman).annotate(
        avg_rating=Coalesce(
            Avg('reviews__rating'),
            Value(0.0),
            output_field=models.FloatField()
        ),
        review_count=Count('reviews', distinct=True)
    ).order_by('-created_at')
    
    paginator = Paginator(services_list, 6) 
    
    page = request.GET.get('page')
    try:
        services = paginator.page(page)
    except PageNotAnInteger:
        services = paginator.page(1)
    except EmptyPage:
        services = paginator.page(paginator.num_pages)
    
    return render(request, 'craftsman_dasboard.html', { 
        'form': form,
        'services': services,
        'craftsman': craftsman,
        'editing_service': editing_service
    })

@login_required
def craftsman_profile(request):
    try:
        craftsman = request.user.userprofile.craftsmanprofile
    except:
        logger.error(f"CraftsmanProfile not found for user {request.user}")
        messages.error(request, "Profile not found. Please contact support.")
        return redirect('home')
    
    profile_complete = craftsman.has_complete_profile()
    
    
    delete_profile = request.GET.get('delete')
    if delete_profile == 'true':
        try:
            
            business_name = craftsman.business_name
            craftsman.delete()
            messages.success(request, f"Profile '{business_name}' has been deleted successfully!")
            return redirect('home')
        except Exception as e:
            logger.error(f"Error deleting profile: {str(e)}")
            messages.error(request, "Error deleting profile. Please try again.")
            return redirect('craftsman_profile')
    
    if request.method == 'POST':
        form = CraftsmanProfileForm(request.POST, request.FILES, instance=craftsman)
        
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('craftsman_profile')
            except Exception as e:
                logger.error(f"Error saving profile: {str(e)}")
                messages.error(request, "Error saving profile. Please try again.")
        else:
            logger.error(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CraftsmanProfileForm(instance=craftsman)
    
    context = {
        'craftsman': craftsman,
        'form': form,
        'profile_complete': profile_complete,
    }
    
    return render(request, 'craftsman_profile.html', context)

def craftsman_public_profile(request, craftsman_id):

    craftsman = get_object_or_404(
        CraftsmanProfile.objects.select_related(
            'user_profile', 
            'user_profile__user'
        ),
        id=craftsman_id
        # Removed: is_verified=True
    )
    
    # Get craftsman's services with ratings and review counts
    services = Service.objects.filter(
        craftsman=craftsman,
        service_status='Active'
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-created_at')
    
    # Paginate services
    paginator = Paginator(services, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate overall craftsman stats
    total_reviews = Review.objects.filter(service__craftsman=craftsman).count()
    avg_rating = Review.objects.filter(
        service__craftsman=craftsman
    ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    craftsman_stats = {
        'total_services': services.count(),
        'total_reviews': total_reviews,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'member_since': craftsman.created_at
    }
    
    context = {
        'craftsman': craftsman,
        'services': page_obj,
        'craftsman_stats': craftsman_stats,
    }
    
    return render(request, 'craftsman_public_profile.html', context)

@login_required
def customer_profile(request):
    try:
        customer = request.user.userprofile.customerprofile
        profile_complete = bool(
            customer.address and 
            customer.city and 
            customer.state and 
            customer.phone
        )
    except CustomerProfile.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('home')

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=customer)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('customer_profile')
            except Exception as e:
                logger.error(f"Error saving customer profile: {str(e)}")
                messages.error(request, "Error saving profile. Please try again.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomerProfileForm(instance=customer)

    context = {
        'customer': customer,
        'form': form,
        'profile_complete': profile_complete,
    }
    
    return render(request, 'customer_profile.html', context)

@login_required
def saved_services(request):
    try:
        customer = request.user.userprofile.customerprofile
        saved_services_list = SavedService.objects.filter(
            customer=customer
        ).select_related(
            'service',
            'service__craftsman',
            'service__craftsman__user_profile'
        ).order_by('-created_at')
        
        # Pagination
        paginator = Paginator(saved_services_list, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
    except CustomerProfile.DoesNotExist:
        messages.error(request, "Customer profile not found.")
        return redirect('home')
    
    context = {
        'page_obj': page_obj,
        'saved_services': page_obj,
    }
    
    return render(request, 'saved_services.html', context)

@login_required
def save_service(request, service_id):
    if request.method == 'POST':
        try:
            customer = request.user.userprofile.customerprofile
            service = Service.objects.get(id=service_id)
            
            
            if SavedService.objects.filter(customer=customer, service=service).exists():
                messages.info(request, "Service already saved.")
            else:
                SavedService.objects.create(customer=customer, service=service)
                messages.success(request, "Service saved successfully!")
                
        except CustomerProfile.DoesNotExist:
            messages.error(request, "Customer profile not found.")
        except Service.DoesNotExist:
            messages.error(request, "Service not found.")
        except Exception as e:
            messages.error(request, "Error saving service.")
    
    return redirect(request.META.get('HTTP_REFERER', 'customer_dashboard'))

@login_required
def unsave_service(request, service_id):
    if request.method == 'POST':
        try:
            customer = request.user.userprofile.customerprofile
            service = Service.objects.get(id=service_id)
            
            saved_service = SavedService.objects.filter(customer=customer, service=service)
            if saved_service.exists():
                saved_service.delete()
                messages.success(request, "Service removed from saved list.")
            else:
                messages.info(request, "Service was not in your saved list.")
                
        except CustomerProfile.DoesNotExist:
            messages.error(request, "Customer profile not found.")
        except Service.DoesNotExist:
            messages.error(request, "Service not found.")
        except Exception as e:
            messages.error(request, "Error removing service.")
    
    return redirect(request.META.get('HTTP_REFERER', 'saved_services'))

@login_required
def craftsman_ad_boost(request):
    return render(request, 'craftsman_ad_boost.html')

def user_logout(request):
    auth_logout(request)
    return redirect('signin')