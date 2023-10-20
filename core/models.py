from django.contrib.auth.models import User
from django.db import models


class Challenger(models.Model):
    STATUS_CHOICES = (
        ("J", "Junior"),
        ("S", "Senior"),
        ("P", "Pro"),
    )
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name_persian = models.CharField(max_length=50)
    last_name_persian = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=11)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, default='M')
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, default='J')
    is_workshop_attender = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    bio = models.TextField(max_length=500, blank=True)
    university = models.TextField(max_length=100, blank=True)
    national_code = models.TextField(max_length=10, blank=True)
    confirmation_code = models.CharField(max_length=5, blank=True)
    is_confirmed = models.BooleanField(default=False)
    password_reset_code = models.CharField(max_length=5, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} {self.get_status_display()}'


class Group(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True)
    judge_password = models.TextField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.name}'


class Membership(models.Model):
    STATUS_CHOICES = (
        ("A", "Accepted"),
        ("P", "Pending"),
        ("R", "Rejected"),
    )
    ROLES_CHOICES = (
        ("M", "Member"),
        ("L", "Leader"),
    )

    challenger = models.ForeignKey(Challenger, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=ROLES_CHOICES,
                            blank=True, default='M')
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, blank=True, default='P')

    def __str__(self):
        return f'{self.challenger} {self.group} {self.get_status_display()} {self.get_role_display()}'
