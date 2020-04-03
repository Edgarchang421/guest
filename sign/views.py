from .models import Event , Guest
from .serializers import EventSerializer , GuestSerializer
from rest_framework import generics

class EventList(generics.ListCreateAPIView):
	query = Event.objects.all()
	serializers_class = EventSerializer
	
class EventDetail(generics.RetrieveUpdateDestroyAPIView):
	query = Event.objects.all()
	serializers_class = EventSerializer
	
class GuestList(generics.ListCreateAPIView):
	query = Guest.objects.all()
	serializers_class = GuestSerializer
	
class GuestDetail(generics.RetrieveUpdateDestroyAPIView):
	query = Guest.objects.all()
	serializers_class = GuestSerializer