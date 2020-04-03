from django.urls import path
from . import views

urlpatterns = [
	path('Events/', views.EventList.as_view()),
	path('Event/<int:pk>/', views.EventDetail.as_view()),
	path('Guests/', views.GuestList.as_view()),
	path('Guest/<int:pk>/', views.GuestDetail.as_view()),
	]