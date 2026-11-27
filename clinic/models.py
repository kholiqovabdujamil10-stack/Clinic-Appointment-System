from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.

class EmailConfirm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    def __str__(self):
        return self.user.username


class Specialization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=150)
    specialization_id = models.ForeignKey(Specialization, on_delete=models.CASCADE)
    experience = models.PositiveIntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='doctors/')
    created_at = models.TimeField(default=datetime.now)
    
    class Meta:
        permissions = [
            ('can_add_doctor', 'User can add doctor'),
            ('can_change_doctor', 'User can change doctor'),
            ('can_delete_doctor', 'User can delete doctor'),
            ('can_view_doctor', 'User can view doctor')
        ]

    def __str__(self):
        return self.name


class Appointment(models.Model):
    CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled')
    ]

    patient_id = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=CHOICES, default='Pending')
    created_at = models.TimeField(default=datetime.now)

    class Meta:
        permissions = [
            ('can_add_appointment', 'User can book appointment'),
            ('can_change_appointment', 'User can change appointment'),
            ('can_delete_appointment', 'User can cancel appointment'),
            ('can_view_appointment', 'User can view appointment')
        ]
    def __str__(self):
        return f'({self.patient_id.username} - {self.doctor_id.name})'

class Review(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient.username} - {self.doctor.name}'