from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),    # as we want if someone tries to go to 'accounts/' endpoint take them to dashboard
    
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),

    path('resetPassword_validate/<uidb64>/<token>', views.resetPassword_validate, name='resetPassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),

    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_details/<int:order_id>', views.order_details, name='order_details'),
]