from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('attendee', 'Attendee'),
        ('organizer', 'Organizer'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )

    name         = models.CharField(max_length=255)
    email        = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role         = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    date_joined  = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.role})"