# guest
使用djangorestframework建立API，透過locust進行效能測試  

## models
```
from django.db import models

# Create your models here.

class Event(models.Model):
	name = models.CharField(max_length=100)
	limit = models.PositiveIntegerField()
	status = models.BooleanField()
	address = models.CharField(max_length=200)
	start_time = models.DateTimeField('events time')
	create_time = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.name
		
class Guest(models.Model):
	event = models.ForeignKey(Event , on_delete = models.CASCADE)
	realname = models.CharField(max_length=64)
	phone = models.CharField(max_length=16)
	email = models.EmailField()
	sign = models.BooleanField()
	create_time = models.DateTimeField(auto_now=True)
	
	class Meta:
		constraints = [
			models.UniqueConstraint(fields = ['phone' , 'event'] , name='unique_phone_event')
		]
	
	def __str__(self):
		return self.realname
```
Event class儲存會議資料，Guest儲存客戶資料  
Guest使用UniqueConstraint確保一個電話號碼phone field只能遷到一個Event  
  
## serializers
```
from .models import Event , Guest
from rest_framework import serializers

class EventSerializer(serializers.ModelSerializer):
	class Meta:
		model = Event
		fields = ['name' , 'address' , 'start_time' , 'limit' , 'status']
		
class GuestSerializer(serializers.ModelSerializer):
	class Meta:
		model = Guest
		fields = ['realname' , 'phone' , 'email' , 'sign' , 'event']
```
使用serializers.ModelSerializer建立view需要的serializer  

## views
```
from .models import Event , Guest
from .serializers import EventSerializer , GuestSerializer
from rest_framework import generics

class EventList(generics.ListCreateAPIView):
	queryset = Event.objects.all()
	serializer_class = EventSerializer
	
class EventDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Event.objects.all()
	serializer_class = EventSerializer
	
class GuestList(generics.ListCreateAPIView):
	queryset = Guest.objects.all()
	serializer_class = GuestSerializer
	
class GuestDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Guest.objects.all()
	serializer_class = GuestSerializer
```
使用generics.ListCreateAPIView以及generics.RetrieveUpdateDestroyAPIView建立view    
  
## sign/urls
```
from django.urls import path
from . import views

urlpatterns = [
	path('Events/', views.EventList.as_view()),
	path('Event/<int:pk>/', views.EventDetail.as_view()),
	path('Guests/', views.GuestList.as_view()),
	path('Guest/<int:pk>/', views.GuestDetail.as_view()),
	]
```
為每一個class-based view建立url  

## guest/settings
```
REST_FRAMEWORK = {
	'DEFAULT_PERMISSION_CLASSES': [
		'rest_framework.permissions.IsAuthenticated',
	],
	'DEFAULT_AUTHENTICATION_CLASSES': [
		'rest_framework_simplejwt.authentication.JWTAuthentication'
	]
}
```
在settings.py中設定所有view的驗證機制為json web token，permission為只有驗證過的user可以讀寫  
  
```
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```
設定djangorestframework-simplejwt套件提供的json web token的access token會在一分鐘後過期，refresh token會在一天後過期  
  
### mysql設定
OS為ubuntu18.04 LTS  
使用sudo apt install mysql-server mysql-client python3-dev libmysqlclient-dev安裝mysql以及相關驅動程式  
使用pip install mysqlclient安裝python驅動mysql所需要的套件  
參考自django官方網站:  
https://docs.djangoproject.com/en/3.0/ref/databases/#mysql-db-api-drivers    
  
接著設定project中的settings.py
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'guest',
		'HOST': '127.0.0.1',
		'PORT': '3306',
		'USER': 'edgar',
		'PASSWORD': 'ken2798315601',
		'OPTIONS':{
			'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
		},
    }
}
```
  
安裝好mysql之後，使用sudo mysql -u root -p登入mysql shell  
接著使用SQL命令建立新的user  
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'newpassword';  
因為root帳號在mysql系統中的登入驗證為auth_socket  
不適合django使用，所以要新增user  
  
新增好user之後，使用root帳號新增資料庫  
CREATE DATABASE 'newdatabase';  

給予新增的user此資料庫的讀寫權限  
GRANT ALL PRIVILEGES ON newdatabase.* TO 'newuser'@'localhost';  
FLUSH PRIVILEGES;  

如此一來django即可連線到此資料庫  
  
然後使用python manage.py makemigrations和python manage.py migrate這兩個指令  
將models.py中定義好的資料結構建立到mysql database中的table    
  
因為要進行效能測試，資料庫中不會只有很少的資料  
但是要手動增加幾千筆資料太過耗時  
所以使用python生成SQL命令，然後在mysql shell中新增資料  

因為要自動insert資料，可以透過SQLstatement使得sign_event和sign_guest兩張資料表中的create_time會直接抓取insert時的時間   
```
alter table `sign_event` change `create_time ` `create_time` timestamp not null default current_timestamp
alter table `sign_guest` change `create_time ` `create_time` timestamp not null default current_timestamp
```
以下為用來生成SQL statement的python程式  
```
import random

f = open("guests.txt",'w')

f.write('INSERT INTO sign_guest (realname , phone , email , sign , event_id) VALUES')
f.write('\n')

for i in range(1,3001):
	str_i = str(i)
	realname = "edgar" + str_i
	phone = 13800110000 + i
	email = "edgar" + str_i + "@gmail.com"
	sql = '("' + realname + '",' + str(phone) + ',"' + email + '",0,' + str(random.randint(1,2)) + '),'
	f.write(sql)
	f.write("\n")
	
f.write(";")
f.close()
```
因為要開啟guest.txt，所以在此python檔的同一目錄下新增guest.txt  
因為需要新增上千筆資料，所以不應該使用單一條命令新增一筆   
使用bulk insert的效能會比較好  
https://www.geeksengine.com/database/data-manipulation/bulk-insert.php  

所以INSERT INTO只要write一次即可  
迴圈中則是生成guest的資料

完成後將 .txt檔中的SQL Statement複製到mysql shell中即可生成資料  
  
# locust
locust是使用python寫成的效能測試工具  
https://docs.locust.io/en/stable/index.html  

```
from locust import HttpLocust , TaskSet , task , between
import random
import json

class UserBehavior(TaskSet):
	
	def on_start(self):
		self.login()
		
	def login(self):
		'''
		##因為有CSRF保護機制，所以要先獲取CSRF token
		response = self.client.get('/api-auth/login/')
		csrftoken = response.cookies['csrftoken']
		
		self.client.post('/api-auth/login/?next=/Events/' , 
			{'username':'admin' , 'password':'password'},
			headers={'X-CSRFToken': csrftoken}
			)
		'''	
		
		##改為json web token驗證
		jsonwebtoken_response = self.client.post('/api/token/', 
			json={'username': 'admin', 'password': 'password'}
		)
		self.json_web_token = json.loads(jsonwebtoken_response.text)
		self.access_token = self.json_web_token['access']
		self.refresh_token = self.json_web_token['refresh']
	
	def use_refresh_token_get_new_access_token(self):
		use_refresh_token_response = self.client.post('/api/token/refresh/', 
			json={'refresh':self.refresh_token}
			)
		refreshed_access_token = json.loads(use_refresh_token_response.text)
		self.access_token = refreshed_access_token['access']
	
	@task
	def event_list(self):
		response = self.client.get('/Events/',headers = {'Authorization': 'Bearer ' + self.access_token})
		if response.status_code == 401:
			self.use_refresh_token_get_new_access_token()
			
	'''	
	@task
	def guest_list(self):
		self.client.get('/Guests/?limit=50&offset=1000')
	
	@task
	def event_detail(self):
		self.client.get('/Event/' + str(random.randint(1,2)) +  '/')
		
	@task
	def guest_detail(self):
		self.client.get('/Guest/7895/')
	'''
class WebsiteUser(HttpLocust):
	task_set = UserBehavior
	wait_time = between(3 , 6)
```

