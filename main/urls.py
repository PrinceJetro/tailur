from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page URL 
    path('accounts/login/', views.login_view, name='login'),  # Login URL
    path('logout/', views.logout_view, name='logout'),  # Logout URL
    path('register/', views.register, name='register'),  # Registration URL
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard URL
    path('add_client/', views.add_client, name='add_client'),  # Add client URL
    path('client_profile/<int:client_id>/', views.client_profile, name='client_profile'),  # Client profile URL
    path('clients/', views.list_clients, name='list_clients'),  # List clients URL
    path('orders/', views.list_orders, name='list_orders'),  # List orders URL
    path('add_measurements/<int:client_id>', views.add_measurements, name='add_measurements'),  # Add measurements URL
    path('add_order/', views.add_order, name='add_order'),  # Add order URL
    path('orders/<int:order_id>/update/', views.update_order, name='update_order'),
    path('orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),  # Delete order URL
    path('order_details/<int:order_id>/', views.order_details, name='order_details'),  # Order details URL
    path('orders/<int:order_id>/pdf/', views.order_details_pdf, name='order_details_pdf'),
]
