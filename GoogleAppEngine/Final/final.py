import webapp2
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
import json



class User(ndb.Model):
	username = ndb.StringProperty(required=True)
	name = ndb.StringProperty(required=True)
	ID = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)


class Weather(ndb.Model):
	name = ndb.StringProperty(required=True)
	ID = ndb.StringProperty(required=True)
	city = ndb.StringProperty(required=True)
	latitude = ndb.StringProperty(required=True)
	longitude = ndb.StringProperty(required=True)
	temp = ndb.StringProperty(required=True)



########################################
class UserHandler(webapp2.RequestHandler):
	route = '/user/'


	def create(self):
		p_key = ndb.Key(User, "p_user")
		data = json.loads(self.request.body)
		token = data['token']
		user_data = self.get_user_data(token);
		if not self.check_user_exist(user_data['id']):
			user = User(username=data['username'],
						name=user_data['name']['givenName'],
						ID=user_data['id'],
						email=user_data['emails'][0]['value'],
						parent=p_key
						)
			user.put()
			u_dict = user.to_dict()
			u_dict['id'] = user.key.urlsafe()
			return u_dict


	def get_user_data(self,token):
		headers = {'Authorization':"Bearer "+token}
		result = urlfetch.fetch(url='https://www.googleapis.com/plus/v1/people/me',
									method=urlfetch.GET,
									headers=headers)
		return json.loads(result.content)


	def check_user_exist(self,ID):
		check = False
		for u in User.query():
			u_d = u.to_dict()
			if (u_d['ID'] == ID):
				check = True
		return check


	def post(self):
		try:
			user = self.create()
			if user:
				self.response.write(json.dumps(user))
				self.response.set_status(201)
			else:
				self.response.set_status(403)
				self.response.write("User already exists")
		except:
			self.response.set_status(400)
			self.response.write("Failed to create user")



	def get(self, token):
		try:
			user_data = self.get_user_data(token)
			try:
				# User.query()[0]
				for u in User.query():
					u_dict = u.to_dict()
					if u_dict['ID'] == user_data['id']:
						self.response.set_status(200)
						self.response.write(u_dict)
			except:
				self.response.set_status(202)
				self.response.write("no users exist")

		except:
			self.response.set_status(400)
			return self.response.write("user does not exist")


	def patch(self):
		try:
			data = json.loads(self.request.body)
			user_data = self.get_user_data(data['token'])

			if User.query():
				for u in User.query():
					u_d = u.to_dict()
					if(user_data['id'] == u_d['ID']):
						u_key = ndb.Key(urlsafe=u.key.urlsafe())
						uget = u_key.get()
						try:
							if data['username']:
								uget.username = data['username']
								uget.put()
						except: pass
						try:
							if data['email']:
								uget.email = str(data['email'])
								uget.put()
						except: pass
						ue = ndb.Key(urlsafe=u.key.urlsafe()).get()
						ue_dict = ue.to_dict()
						ue_dict['id'] = self.route+u.key.urlsafe()
						self.response.set_status(202)
						self.response.write(json.dumps(ue_dict))
		except:
			self.response.set_status(400)
			self.response.write("Missing raw json")



	def delete(self, res):
		try:
			token = res
			user_data = self.get_user_data(token)
			try:
				# User.query()[0]
				for u in User.query():
					u_d = u.to_dict()
					if(user_data['id'] == u_d['ID']):
						u_key = ndb.Key(urlsafe=u.key.urlsafe())
						uget = u_key.get()
						uget.key.delete()
						self.response.set_status(203)
						self.response.write("user deleted")
			except:
				self.response.set_status(203)
				return self.response.write("no users exist")
		except:
			self.response.set_status(402)
			self.response.write("bad token")






########################################
class WeatherHandler(webapp2.RequestHandler):
	route = '/weather/'

	def create(self):
		p_key = ndb.Key(Weather, "p_weather")
		data = json.loads(self.request.body)
		token = data['token']
		user_data = self.get_user_data(token);
		try:
			if self.check_user_exist(user_data['id']):
				if not self.check_name_exist(user_data, data['name_id']):
					weather_data = self.get_weather_data(data)
					weather = Weather(name=data['name_id'],
									  ID=user_data['id'],
									  city=weather_data['name'],
									  latitude=str(weather_data['coord']['lat']),
									  longitude=str(weather_data['coord']['lon']),
									  temp=str(weather_data['main']['temp']),
									  parent=p_key)
					weather.put()
					w_dict = weather.to_dict()
					w_dict['id'] = weather.key.urlsafe()
					return w_dict
				else:
					self.response.set_status(403)
					self.response.write("name_id already exists")
		except:
			self.response.set_status(403)
			self.response.write("User does not exist")




	def post(self):
		# try:
			weather = self.create()
			if weather:
				self.response.write(json.dumps(weather))
				self.response.set_status(201)
			
		# except:
		# 	self.response.set_status(400)
		# 	self.response.write("Failed to add weather")



	def get(self,token):
		lst = []
		user_data = self.get_user_data(token)
		try: 
			if self.check_user_exist(user_data['id']):
				for u in Weather.query():
					u_d = u.to_dict()
					if (u_d['ID'] == user_data['id']):
						u_d['id'] = self.route+u.key.urlsafe() 
						lst.append(json.dumps(u_d))
			else:
				self.response.set_status(403)
				self.response.write("User does not exist")
		finally:
			res = ""
			for l in lst:
				res+=str(l)+"\n"
			return self.response.write(res)


	def delete(self, res):
		try:
			token = res.split("/")[0]
			name_id = res.split("/")[1]
			user_data = self.get_user_data(token)
			if Weather.query():
				if self.check_name_exist(user_data,name_id):
					for w in Weather.query():
						w_d = w.to_dict()
						if(w_d['name'] == name_id and user_data['id'] == w_d['ID']):
							try:
								w_key = ndb.Key(urlsafe=w.key.urlsafe())
								wget = w_key.get()
								wget.key.delete()
								self.response.set_status(203)
								self.response.write("weather deleted")
							except:
								self.response.set_status(400)
								self.response.write("weather does not exist")
				else:
					self.response.set_status(400)
					self.response.write("weather does not exist")
			else:
				self.response.set_status(400)
				self.response.write("no weather objects")
		except:
			self.response.set_status(400)
			self.response.write("missing name_id")

		


	def patch(self):
		try:
			data = json.loads(self.request.body)
			user_data = self.get_user_data(data['token'])

			if Weather.query():
				for w in Weather.query():
					w_d = w.to_dict()
					if(w_d['name'] == data['name_id'] and user_data['id'] == w_d['ID']):
						w_key = ndb.Key(urlsafe=w.key.urlsafe())
						wget = w_key.get()
						try:
							if data['name']:
								wget.name = data['name']
								wget.put()
						except: pass
						try:
							if data['lat'] and data['lon']:
								weather_data = self.get_weather_data(data)
								wget.latitude = str(weather_data['coord']['lat'])
								wget.longitude = str(weather_data['coord']['lon'])
								wget.city = weather_data['name']
								wget.temp = str(weather_data['main']['temp'])
								wget.put()
						except: pass
						we = ndb.Key(urlsafe=w.key.urlsafe()).get()
						we_dict = we.to_dict()
						we_dict['id'] = self.route+w.key.urlsafe()
						self.response.set_status(202)
						self.response.write(json.dumps(we_dict))
		except:
			self.response.set_status(400)
			self.response.write("Missing raw json")




	def check_user_exist(self,ID):
		for u in User.query():
			u_d = u.to_dict()
			if (u_d['ID'] == ID):
				return True


	def check_name_exist(self,user_data,name_id):
		if Weather.query():
			for w in Weather.query():
				w_d = w.to_dict()
				# return self.response.write(w_d)
				if(w_d['name'] == name_id and user_data['id'] == w_d['ID']):
					return True
		else:
			return True

	
	def get_weather_data(self,data):
		apikey = "629c66bbfbe510c270df3aa183819bb0"
		result = urlfetch.fetch(url='http://api.openweathermap.org/data/2.5/weather?lat='
			+data['lat']
			+'&lon='
			+data['lon']+'&units=metric&APPID='+apikey,method=urlfetch.GET)
		return json.loads(result.content)

	
	def get_user_data(self,token):
		headers = {'Authorization':"Bearer "+token}
		result = urlfetch.fetch(url='https://www.googleapis.com/plus/v1/people/me',
									method=urlfetch.GET,
									headers=headers)
		return json.loads(result.content)






###################
class Main(webapp2.RequestHandler):
    def get(self):
        self.response.write('Welcome!')

def allow_patch():
	allowed_methods = webapp2.WSGIApplication.allowed_methods
	new_allowed_methods = allowed_methods.union(('PATCH',))
	webapp2.WSGIApplication.allowed_methods = new_allowed_methods
allow_patch()

app = webapp2.WSGIApplication([
	('/', Main),
    ('/user', UserHandler),
    ('/user/', UserHandler),
    ('/user/(.*)', UserHandler),
    ('/weather/', WeatherHandler),
    ('/weather/(.*)', WeatherHandler),
], debug=True)


