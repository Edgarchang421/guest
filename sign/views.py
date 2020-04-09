from .models import Event , Guest
from .serializers import EventSerializer , GuestSerializer
from rest_framework import generics , permissions
from rest_framework import filters

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
	filter_backends = [filters.OrderingFilter]
	ordering_fields = ['create_time','id']
	ordering = ['id']
	
class GuestDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Guest.objects.all()
	serializer_class = GuestSerializer