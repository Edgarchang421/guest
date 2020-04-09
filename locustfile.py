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