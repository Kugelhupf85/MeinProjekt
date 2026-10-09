"""
Security Management URL Configuration.
"""
from django.urls import path
from ...views.security import (
    SecurityQuestionListView, user_security_answers_view,
    set_security_answers_view, clear_security_answers_view,
    get_user_security_questions_view, SecurityQuestionManagementView,
    toggle_security_question_view
)

urlpatterns = [
    # Security Questions
    path('security-questions/', SecurityQuestionListView.as_view(), name='security-questions'),
    path('user-security-questions/', get_user_security_questions_view, name='user-security-questions'),
    
    # User Security Answers
    path('my-security-answers/', user_security_answers_view, name='my-security-answers'),
    path('set-security-answers/', set_security_answers_view, name='set-security-answers'),
    path('clear-security-answers/', clear_security_answers_view, name='clear-security-answers'),
    
    # Admin Security Question Management
    path('admin/security-questions/', SecurityQuestionManagementView.as_view(), name='admin-security-questions'),
    path('admin/security-questions/<int:question_id>/toggle/', toggle_security_question_view, name='toggle-security-question'),
] 