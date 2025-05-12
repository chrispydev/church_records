from django.db import models
from django.urls import reverse


class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    hall_or_hostel = models.CharField(max_length=100, default='hall or hostel')
    room_number = models.CharField(max_length=20, default='R10')
    year_of_enrollment = models.CharField(max_length=20, default='2025')
    telephone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('member-detail', kwargs={'pk': self.pk})
