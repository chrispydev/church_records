from django.urls import path
from . import views

urlpatterns = [
    path('', views.AppointmentCreateView.as_view(), name='appointment-create'),
    path('confirmation/', views.AppointmentConfirmationView.as_view(),
         name='appointment-confirmation'),
    path('time-slots/', views.AppointmentTimeSlotsView.as_view(),
         name='appointment-time-slots'),
    path('home/', views.home, name='appointments-home'),
]
