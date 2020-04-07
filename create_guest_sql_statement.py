import random

f = open('guests.txt','w')

f.write('INSERT INTO sign_guest (realname , phone , email , sign , event_id) VALUES')
f.write('\n')

for i in range(1,3001):
	str_i = str(i)
	realname = 'edgar' + str_i
	phone = 13800110000 + i
	email = 'edgar' + str_i + '@gmail.com'
	sql = '('' + realname + '',' + str(phone) + ','' + email + '',0,' + str(random.randint(1,2)) + '),'
	f.write(sql)
	f.write('\n')
	
f.write(';')
f.close()