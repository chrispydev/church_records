from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, View
from django.contrib import messages
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
import datetime
import json

from .models import Appointment, AvailableDay, BookingSettings
from .forms import AppointmentForm

class AppointmentCreateView(CreateView):
    """View for creating a new appointment"""
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Check if booking system is enabled"""
        # Get booking settings
        booking_settings = BookingSettings.get_settings()
        self.booking_settings = booking_settings
        
        # If system is disabled, show message and redirect
        if not booking_settings.is_enabled:
            messages.error(request, "The appointment booking system is currently disabled.")
            return redirect('home')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Add available days and booking settings to context"""
        context = super().get_context_data(**kwargs)
        
        # Add page title
        context['title'] = 'Book an Appointment'
        
        # Add booking settings
        context['booking_settings'] = self.booking_settings
        
        # Get available days to help with date selection
        form = context.get('form')
        if form:
            available_days = form.get_available_days()
            context['available_days'] = available_days
            
            # Format days for JavaScript (to disable unavailable days)
            available_days_js = []
            for day in available_days:
                available_days_js.append(day['formatted'])
            context['available_days_js'] = json.dumps(available_days_js)
        
        return context
    
    def form_valid(self, form):
        """Handle valid form"""
        # Set appointment to pending status
        form.instance.status = 'pending'
        
        # Show success message
        messages.success(
            self.request, 
            "Your appointment has been scheduled successfully! "
            "Please check your email for confirmation details."
        )
        
        # Save the appointment
        response = super().form_valid(form)
        
        # Store appointment ID in session for confirmation view
        self.request.session['appointment_id'] = self.object.id
        
        return response
    
    def get_success_url(self):
        """Redirect to confirmation page after successful booking"""
        return reverse('appointment-confirmation')


class AppointmentConfirmationView(DetailView):
    """View for displaying appointment confirmation"""
    model = Appointment
    template_name = 'appointments/appointment_confirmation.html'
    context_object_name = 'appointment'
    
    def get_object(self):
        """Get appointment from session"""
        appointment_id = self.request.session.get('appointment_id')
        if not appointment_id:
            raise Http404("No appointment found.")
        
        # Clear session data
        if 'appointment_id' in self.request.session:
            del self.request.session['appointment_id']
        
        # Get appointment
        return get_object_or_404(Appointment, id=appointment_id)
    
    def get_context_data(self, **kwargs):
        """Add additional context"""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Appointment Confirmation'
        return context


class AppointmentTimeSlotsView(View):
    """AJAX view for getting available time slots for a date"""
    
    def get(self, request, *args, **kwargs):
        """Handle GET request for time slots"""
        # Check if booking is enabled
        booking_settings = BookingSettings.get_settings()
        if not booking_settings.is_enabled:
            return JsonResponse({'error': 'Booking system is disabled'}, status=400)
        
        # Get date from request
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'No date provided'}, status=400)
        
        try:
            # Parse date
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check if date is in the past
            today = datetime.date.today()
            if selected_date < today:
                return JsonResponse({'error': 'Cannot book appointments in the past'}, status=400)
            
            # Get time slots for the date
            form = AppointmentForm()
            time_slots = form.get_time_slots_for_day(selected_date)
            
            # Check if any slots available
            if not time_slots:
                day_name = selected_date.strftime('%A')
                return JsonResponse({
                    'error': f'No available time slots on {day_name}, {selected_date.strftime("%B %d, %Y")}'
                }, status=404)
            
            # Format slots for response
            formatted_slots = []
            for slot in time_slots:
                formatted_slots.append({
                    'value': slot['value'],
                    'text': slot['formatted']
                })
            
            return JsonResponse({'slots': formatted_slots})
            
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)


# Simple home view that redirects to the booking form
def home(request):
    return redirect('appointment-create')
