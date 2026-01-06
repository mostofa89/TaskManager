from django.db import models
from django.contrib.auth.models import User
import random
import string

class PasswordResetCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reset_code')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Reset code for {self.user.username}"
    
    @staticmethod
    def generate_code():
        """Generate a random 6-digit code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        """Check if code is older than 15 minutes"""
        from django.utils import timezone
        from datetime import timedelta
        return (timezone.now() - self.created_at) > timedelta(minutes=15)