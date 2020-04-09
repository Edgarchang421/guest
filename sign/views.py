from .models import Event , Guest
from .serializers import EventSerializer , GuestSerializer
from rest_framework import generics , permissions

class EventList(generics.ListCreateAPIView):
	queryset = Event.objects.all()
	serializer_class = EventSerializer
	
class EventDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Event.objects.all()
	serializer_class = EventSerializer
	
class GuestList(generics.ListCreateAPIView):
	#permission_classes = [permissions.AllowAny]
	queryset = Guest.objects.all()
	serializer_class = GuestSerializer
	
class GuestDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Guest.objects.all()
	serializer_class = GuestSerializer