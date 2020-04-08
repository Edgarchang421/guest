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
	