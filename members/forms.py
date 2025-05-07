from django import forms
from .models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'room_number', 'telephone_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your room number'}),
            'telephone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your telephone number'}),
        }

