from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import send_mail
from datetime import datetime
from random import randint
from .models import *


def registration(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return redirect('registration')
        if User.objects.filter(email=email).exists():
            return redirect('registration')

        user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
        code = str(randint(100000, 999999))
        EmailConfirm.objects.create(user=user, code=code)
        send_mail('Confirm email', f'Your code: {code}', [email])
        
        return redirect('confirm_email')
    
    return render(request, 'clinic/registration.html')


def confirm_email(request):
    if request.method == 'POST':
        username = request.POST['username']
        entered_code = request.POST['code']
        user = User.objects.filter(username=username).first()

        if user:
            code = EmailConfirm.objects.filter(user=user, code=entered_code).first()
            if code:
                user.is_active = True
                user.save()
                code.delete()
                login(request, user)
                return redirect('profile')
        return redirect('confirm_email')
    return render(request, 'clinic/confirm_email.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.groups.filter(name='Doctors').exists():
                return redirect('doctor_profile')
            return redirect('profile')
        return redirect('login')
    return render(request, 'clinic/login.html')


@login_required
def logout_user(request):
    logout(request)
    return redirect('login')


@login_required
def profile(request):
    appointments = Appointment.objects.filter(patient_id=request.user)
    return render(request, 'clinic/profile.html', {'appointments': appointments})


def home(request):
    doctors = Doctor.objects.all()
    specializations = Specialization.objects.all()
    search = request.GET.get('query', '')
    specialization = request.GET.get('specialization')
    sort = request.GET.get('sort', '')

    if search:
        doctors = doctors.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if specialization:
        doctors = doctors.filter(specialization_id_id=specialization)

    if sort == 'experience':
        doctors = doctors.order_by('-experience')
    elif sort == 'experience_low':
        doctors = doctors.order_by('experience')
    return render(request, 'clinic/home.html', {'doctors': doctors, 'specializations': specializations, 'query': search, 'selected_specialization': specialization, 'sort': sort})


def doctor_info(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    reviews = Review.objects.filter(doctor=doctor)
    return render(request, 'clinic/doctor_detail.html', {'doctor': doctor, 'reviews': reviews})


# Доступ к странице только для авторизованных пользователей
# Доступ к странице только для авторизованных пользователей
@login_required
def create_appointment(request, pk):

    # Получаем врача по ID или возвращаем ошибку 404
    doctor = get_object_or_404(Doctor, pk=pk)

    # Проверяем, отправлена ли форма
    if request.method == 'POST':

        # Получаем дату и причину обращения из формы
        date = request.POST.get('appointment_date', '').strip()
        reason = request.POST.get('reason', '').strip()

        # Проверяем, заполнены ли все поля
        if not date or not reason:
            return render(request, 'clinic/book_appointment.html', {'doctor': doctor, 'error': 'Заполните все поля!'})

        # Проверяем формат даты и преобразуем строку в объект datetime
        try:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M')
        except ValueError:
            return render(request, 'clinic/book_appointment.html', {'doctor': doctor, 'error': 'Неправильный формат даты!'})

        # Проверяем, занято ли выбранное время у этого врача
        if Appointment.objects.filter(doctor_id=doctor, appointment_date=date, status__in=['Pending', 'Confirmed']).exists():
            return render(request, 'clinic/book_appointment.html', {'doctor': doctor, 'error': 'Это время уже занято!'})

        # Создаём новую запись на приём к врачу
        Appointment.objects.create(patient_id=request.user, doctor_id=doctor, appointment_date=date, reason=reason)

        # Перенаправляем пользователя на страницу его записей
        return redirect('my_appointments')

    # Если форма ещё не отправлена, отображаем страницу записи
    return render(request, 'clinic/book_appointment.html', {'doctor': doctor})


@login_required
def show_appointments(request):
    appointments = Appointment.objects.filter(patient_id=request.user)
    search = request.GET.get('query', '')
    status = request.GET.get('status', '')
    if search:
        appointments = appointments.filter(Q(doctor_id__name__icontains=search) | Q(reason__icontains=search))

    if status:
        appointments = appointments.filter(status=status)
    return render(request, 'clinic/my_appointments.html', {'appointments': appointments, 'data': search, 'status': status})


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient_id=request.user)
    if request.method == 'POST':
        appointment.status = 'Cancelled'
        appointment.save()
        return redirect('my_appointments')
    return render(request, 'clinic/cancel_appointment.html', {'appointment': appointment})


@login_required
def my_patients(request):
    if not request.user.groups.filter(name='Doctors').exists():
        return redirect('home')

    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor_id=doctor)
    return render(request, 'clinic/my_patients.html', {'appointments': appointments})


@login_required
def change_profile(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            return redirect('edit_profile')

        request.user.username = username
        request.user.email = email
        request.user.save()
        return redirect('profile')
    return render(request, 'clinic/edit_profile.html')


@login_required
def doctor_profile(request):
    if not request.user.groups.filter(name='Doctors').exists():
        return redirect('home')
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor_id=doctor)

    return render(request, 'clinic/doctor_profile.html', {'doctor': doctor, 'appointments': appointments})


@login_required
def change_appointment_status(request, pk):
    if not request.user.groups.filter(name='Doctors').exists():
        return redirect('home')

    doctor = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, pk=pk, doctor_id=doctor)
    if request.method == 'POST':
        status = request.POST['status']
        if status in ['Confirmed', 'Cancelled']:
            appointment.status = status
            appointment.save()
    return redirect('doctor_profile')


@login_required
def edit_doctor(request):
    if not request.user.groups.filter(name='Doctors').exists():
        return redirect('home')

    doctor = get_object_or_404(Doctor, user=request.user)
    if request.method == 'POST':
        doctor.name = request.POST['name']
        doctor.specialization_id = get_object_or_404(Specialization, id=request.POST['specialization'])
        doctor.experience = request.POST['experience']
        doctor.description = request.POST['description']

        if request.FILES.get('image'):
            doctor.image = request.FILES['image']

        doctor.save()
        return redirect('doctor_profile')

    specializations = Specialization.objects.all()
    return render(request, 'clinic/edit_doctor.html', {'doctor': doctor, 'specializations': specializations})


@login_required
def add_review(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        rating = request.POST['rating']
        text = request.POST['text']
        if rating in ['1', '2', '3', '4', '5'] and text:
            Review.objects.create(patient=request.user, doctor=doctor, rating=rating, text=text)
    return redirect('doctor_detail', pk=doctor.id)