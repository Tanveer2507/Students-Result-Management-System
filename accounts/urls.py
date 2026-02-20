from django.urls import path
from . import views

urlpatterns = [
    # Website Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('contact/', views.contact, name='contact'),
    
    # Login Pages
    path('login/', views.login_view, name='login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('login/student/', views.student_login, name='student_login'),
    path('login/teacher/', views.teacher_login, name='teacher_login'),
    path('register/student/', views.student_registration, name='student_registration'),
    path('register/teacher/', views.teacher_registration, name='teacher_registration'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Password Reset
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('forgot-password/admin/', views.admin_forgot_password, name='admin_forgot_password'),
    path('forgot-password/teacher/', views.teacher_forgot_password, name='teacher_forgot_password'),
    path('forgot-password/student/', views.student_forgot_password, name='student_forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
]
