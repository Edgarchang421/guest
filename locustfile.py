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