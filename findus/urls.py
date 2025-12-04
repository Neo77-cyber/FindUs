from django.urls import path
from . import views



urlpatterns = [
    path('', views.home, name='home'),   
    path('signin/', views.signin, name='signin'),
    path('register/', views.register_craftsman, name='register_craftsman'),
    path('change-password/', views.change_password, name='change_password'),
    path('customer-dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('customer-profile/', views.customer_profile, name='customer_profile'), 
    path('save-location/', views.save_user_location, name='save_location'),
    path('craftsman-dashboard/', views.craftsman_dashboard, name='craftsman_dashboard'),
    path('craftsman-profile/', views.craftsman_profile, name='craftsman_profile'),
    path('craftsman/<int:craftsman_id>/', views.craftsman_public_profile, name='craftsman_public_profile'),  
    path('craftsman-ads-boost/', views.craftsman_ad_boost, name='craftsman_ad_boost'), 
    path('saved-services/', views.saved_services, name='saved_services'),
    path('save-service/<int:service_id>/', views.save_service, name='save_service'),
    path('unsave-service/<int:service_id>/', views.unsave_service, name='unsave_service'),   
    path('logout', views.user_logout, name = 'logout'),
    
]