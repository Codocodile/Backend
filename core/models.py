from django.contrib.auth.models import User
from django.db import models


class Challenger(models.Model):
    STATUS_CHOICES = (
        ("S", "Student"),
        ("B", "Beginner"),
        ("A", "Advanced"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, blank=True, default='S')
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} {self.get_status_display()}'


class Group(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500)

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
