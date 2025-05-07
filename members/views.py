from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.contrib import messages
from django.urls import reverse_lazy

from .models import Member
from .forms import MemberForm

class MemberListView(ListView):
    model = Member
    template_name = 'members/member_list.html'
    context_object_name = 'members'
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'All Members'
        return context

class MemberCreateView(CreateView):
    model = Member
    form_class = MemberForm
    template_name = 'members/member_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register New Member'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Member "{form.instance.name}" has been registered successfully!')
        return super().form_valid(form)

class MemberDetailView(DetailView):
    model = Member
    template_name = 'members/member_detail.html'
    context_object_name = 'member'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Member: {self.object.name}'
        return context


# Home view to redirect to member list
def home(request):
    return redirect('member-list')
