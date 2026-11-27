from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    
    path('registration/', registration, name='registration'),
    path('confirm-email/', confirm_email, name='confirm_email'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('profile/', profile, name='profile'),
    
    path('doctor/<int:pk>/', doctor_info, name='doctor_detail'),
    path('doctor-profile/', doctor_profile, name='doctor_profile'),
    path('doctor-profile/edit/', edit_doctor, name='edit_doctor'),

    path('doctor/<int:pk>/appointment/', create_appointment, name='book_appointment'),
    path('appointments/', show_appointments, name='my_appointments'),
    path('appointments/<int:pk>/cancel/', cancel_appointment, name='cancel_appointment'),
    
    path('my-patients/', my_patients, name='my_patients'),
    path('profile/edit/', change_profile, name='edit_profile'),
    
    path('doctor-profile/appointment/<int:pk>/status/', change_appointment_status, name='change_appointment_status'),
    path('doctor/<int:pk>/review/', add_review, name='add_review')
]
