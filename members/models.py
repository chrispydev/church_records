from django.db import models
from django.urls import reverse

class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    room_number = models.CharField(max_length=20)
    telephone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('member-detail', kwargs={'pk': self.pk})
