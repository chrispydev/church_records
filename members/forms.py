from django import forms
from .models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'room_number', 'telephone_number',
                  'hall_or_hostel', 'year_of_enrollment']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'hall_or_hostel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your hall_or_hostel'}),
            'year_of_enrollment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your year_of_enrollment'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your room number'}),
            'telephone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your telephone number'}),
        }
