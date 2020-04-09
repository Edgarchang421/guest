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
Guest使用UniqueConstraint確保一個電話號碼phone field只能簽到一個Event  
  
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
		'rest_framework_simplejwt.authentication.JWTAuthentication',
	],
	'DEFAULT_PAGINATION_CLASS': 
		'rest_framework.pagination.LimitOffsetPagination'
	,
}
```
在settings.py中設定所有view的驗證機制為json web token，permission權限設定為只有驗證過的user可以讀寫   
  
DEFAULT_PAGINATION_CLASS將API的分頁設定為CursorPagination  
CursorPagination相較於LimitOffsetPagination最大的好處是，不會因為資料表過大而導致降地效能  
  
要使用CursorPagination有些地方要稍加注意，第一件事是應該要使用甚麼ordeing排序，在REST framework中的default是 '-created'  
這是建立在假設model instances上會有一個 'created' 的時間戳記timestamp field，並且會顯示成 'timeline'style paginated view  
  
但是也可以透過使用override pagination class 中的 'ordering' attribute  
或者是同時使用 CursorPagination 和 OrderingFilter filter class , 即可在view中指定允許進行排序和用來排序的field  

有了ordering field之後，還需要確定以下的注意事項，才能將cursor pagination的效用完整發揮  

1. ordering field在建立instance之後就不應該被改變，例如timestamp、slug。    
2. ordering field應該要具有唯一性，或者是幾乎唯一，有道毫秒精度的時間戳就是一個很好的例子。  
3. ordering field應該是可以被強制轉換為string的non-nullable value。  
4. ordering field不應該使用float，會很容易導致錯誤，可以改為使用decimals。
5. ordering field需要有database的index。  

因為這些原因，我選擇使用django在建立model instance時會自動新增的 'id' 作為ordering field   
所以先在view中加上filter class
```
ordering_fields = ['id']
ordering = ['id']
```
ordering_fields是允許排序的field  
ordering是default的排序用field  

然後可以使用SQL在MYSQL中確認 id 是否有建立 index  
```
SHOW INDEXES from `tablename`;
```
因為id是主鍵，所以已經建立好index了，如果需要使用別的field建立index，可以使用以下statement  
```
ALTER TABLE `tablename` ADD INDEX ( `indexname` );
```
設定完之後，GET /Guests/ 就會有帶有cursor的next URL可以取的下一頁的資料了  
  
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

因為要自動insert資料，可以透過SQL statement使得sign_event和sign_guest兩張資料表中的create_time會直接抓取insert時的時間   
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
記得在python檔的同一目錄下新增guest.txt  
  
因為需要新增上千筆資料，所以不應該使用單一條命令新增一筆   
使用bulk insert的效能會比較好  
更多bulk insert的說明 :   
https://www.geeksengine.com/database/data-manipulation/bulk-insert.php  

INSERT INTO只要write一次即可  
迴圈中則是生成guest的資料

完成後將 .txt檔中的SQL Statement複製到mysql shell中即可生成資料  
  
# locust
locust是使用python寫成的效能測試工具  
官方文件 :   
https://docs.locust.io/en/stable/index.html  

```
from locust import HttpLocust , TaskSet , task , between
import random
import json

class UserBehavior(TaskSet):
	
	def on_start(self):
		self.get_json_web_token()
		
	def basic_login(self):
		##因為有CSRF保護機制，所以要先獲取CSRF token
		response = self.client.get('/api-auth/login/')
		csrftoken = response.cookies['csrftoken']
		
		self.client.post('/api-auth/login/?next=/Events/' , 
			{'username':'admin' , 'password':'password'},
			headers={'X-CSRFToken': csrftoken}
			)
		
	def get_json_web_token(self):	
		##json web token驗證
		jsonwebtoken_response = self.client.post('/api/token/', 
			json={'username': 'admin', 'password': 'password'}
			)
		
		self.json_web_token = json.loads(jsonwebtoken_response.text)
		self.access_token = self.json_web_token['access']
		self.refresh_token = self.json_web_token['refresh']
		self.JWTheaders = {'Authorization': 'Bearer ' + self.access_token}
	
	def use_refresh_token_get_new_access_token(self):
		refresh_token_response = self.client.post('/api/token/refresh/', 
			json={'refresh':self.refresh_token}
			)
		
		refreshed_access_token = json.loads(refresh_token_response.text)
		self.access_token = refreshed_access_token['access']
		self.JWTheaders = {'Authorization': 'Bearer ' + self.access_token}
	
	@task(0)
	def event_list(self):
		with self.client.get('/Events/' , headers = self.JWTheaders) as response :
			if response.status_code == 401:
				self.use_refresh_token_get_new_access_token()
		
	@task(0)
	def guest_list(self):
		with self.client.get('/Guests/?limit=50&offset=1000' , headers = self.JWTheaders) as response :
			if response.status_code == 401:
				self.use_refresh_token_get_new_access_token()
	
	@task(0)
	def event_detail(self):
		with self.client.get('/Event/' + str(random.randint(1,2)) + '/' , headers = self.JWTheaders) as response :
			if response.status_code == 401:
				self.use_refresh_token_get_new_access_token()
		
	@task(0)
	def guest_detail(self):
		with self.client.get('/Guest/7895/' , headers = self.JWTheaders) as response :
			if response.status_code == 401:
				self.use_refresh_token_get_new_access_token()

class WebsiteUser(HttpLocust):
	task_set = UserBehavior
	wait_time = between(3 , 6)
```
basic_login() 可以使用一般的帳號密碼來驗證，登入API  
因為django有CSRF保護機制，所以使用程式登入時，需要先Get依次此頁面獲得CSRF token  
POST時在把這個token放在headers中，POST才不會失敗  

get_json_web_token() 用來或取得json web token，建立function以便task呼叫  

use_refresh_token_get_new_access_token() 會使用refresh token去刷新access token  
因為access token有時限，超過間token就會失效無法用來驗證user  

@task() 裝飾器可以決定每一個task的執行比例，設定為0時就不會執行  
假如有一個@task(2)、另一個@task(1)，則權重為2的會執行2次、權重為1的只會執行1次  

使用locust主要測試GET method
如果要測試List的POST method或者Detail的Delete Put method，使用亂數會重複相同的使用者，雖然遇到重複的request伺服器也能正常處理

但是如果要測試3000個guest需要花多久的時間完成簽到，則可以換成使用Python的多執行緒Parallelism平行發出requests
```
import requests
import threading
from time import time
import json

## 要測試的domain
base_url = 'http://192.168.1.105:8000/'

## 子執行緒的目標function
def put_sign(start_user , end_user):
	##先取得Json web token
	get_token_response = requests.post(base_url + 'api/token/', 
		json={'username': 'admin', 'password': 'password'}
		)
		
	json_web_token = json.loads(get_token_response.text)
	access_token = json_web_token['access']
	refresh_token = json_web_token['refresh']
	JWTheaders = {'Authorization': 'Bearer ' + access_token}
	
	## 使用PUT method去update嘉賓的簽到狀態sign
	for i in range(start_user , end_user):
		data = {'realname' : 'edgar' + str(i),
			'phone' : 13800110000 + i,
			'email' : 'edgar' + str(i) + '@gmail.com',
			'sign' : True,
			'event' : 1
			}
			
		requests.put(base_url + 'Guest/' + str(i) + '/' , data=data , headers = JWTheaders)

## 建立字典，將要執行PUT的3000個Guest id分成五組
## 因為前面建立mysql時，刪除了兩次，所以是guest的id是6001~9000
## range(x,y)會生成x~y-1的數字
lists = {6001:6601 , 6601:7201 , 7201:7801 , 7801:8401 , 8401:9001}

##子執行緒的列表
threads = []

## 使用for迭代字典的 .items()
## .items會回傳dic中所有的key-value pair，每一對都會以tuple的形式回傳
## .append會把建立的執行緒加到threads列表的最後
## 全部會建立五個執行緒
for start_user , end_user in lists.items():
	t = threading.Thread(target = put_sign , args=(start_user , end_user))
	threads.append(t)
	
if __name__ == '__main__':
	start_time = time()
	
	## 讓前面建立的五個子執行緒開始執行
	for i in range(len(lists)):
		threads[i].start()
	
	##等待五個子執行緒都結束後，再繼續執行後面的程式
	for i in range(len(lists)):
		threads[i].join()
		
	end_time = time()
	
	print('start time : ' + str(start_time))
	print('end time : ' + str(end_time))
	print('run time : ' + str(end_time - start_time))
```
最後的執行結果為  
```
start time : 1586228754.9292247
end time : 1586228889.8274224
run time : 134.89819765090942
```
因為只是使用python manage.py runserver的測試伺服器，所以效能不高  
