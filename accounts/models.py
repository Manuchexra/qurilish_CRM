from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('main_warehouse_admin', 'Main Warehouse Admin'),
        ('warehouse_admin', 'Warehouse Admin'),
        ('main_warehouse_forwarder', 'Main Warehouse Forwarder'),
        ('warehouse_receiver', 'Warehouse Receiver'),
    )
    
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='warehouse_receiver')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.role}"