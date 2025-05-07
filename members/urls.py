from django.urls import path
from . import views

urlpatterns = [
    path('', views.MemberListView.as_view(), name='member-list'),
    path('register/', views.MemberCreateView.as_view(), name='member-create'),
    path('member/<int:pk>/', views.MemberDetailView.as_view(), name='member-detail'),
]
