from .models import Event , Guest
from rest_framework import serializers

class EventSerializer(serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = ['name' , 'address' , 'strart_time' , 'limit' , 'status']
		
class GuestSerializer(serializers.ModelSerializer):
	class Meta:
		model = Guest
		fields = ['realname' , 'phone' , 'email' , 'sign' , 'event']