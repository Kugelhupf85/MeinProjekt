"""
Authentication URL Configuration.
"""
from django.urls import path
from ...views.auth import (
    login_view, logout_view, check_auth_view, refresh_token_view,
    register_view, verify_email_view, resend_verification_view,
    change_password_view, reset_password_request_view, reset_password_with_security_view
)

urlpatterns = [
    # Authentication
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('check/', check_auth_view, name='check-auth'),
    path('refresh/', refresh_token_view, name='refresh-token'),
    
    # Registration
    path('register/', register_view, name='register'),
    path('verify-email/', verify_email_view, name='verify-email'),
    path('resend-verification/', resend_verification_view, name='resend-verification'),
    
    # Password Management
    path('change-password/', change_password_view, name='change-password'),
    path('reset-password-request/', reset_password_request_view, name='reset-password-request'),
    path('reset-password-security/', reset_password_with_security_view, name='reset-password-security'),
] 