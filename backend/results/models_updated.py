from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
import logging

security_logger = logging.getLogger('security')

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    roll_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return f"{self.username} ({self.role})"
