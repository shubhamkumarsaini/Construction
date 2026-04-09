from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

# ✅ Custom User Manager
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        # default values
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


# ✅ Custom User Model
class User(AbstractUser):
    username = None  # remove username

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('accountant', 'Accountant'),
        ('supervisor', 'Supervisor'),
    )

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='manager')

    phone = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)

    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    # Django permissions fields already included in AbstractUser:
    # is_active, is_staff, is_superuser

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email
