import webapp2
from google.appengine.ext import ndb
import json



class Boat(ndb.Model):
	name = ndb.StringProperty(required=True)
	b_type = ndb.StringProperty(required=True)
	length = ndb.IntegerProperty(required=True)
	atsea = ndb.BooleanProperty()

class Slip(ndb.Model):
	number = ndb.IntegerProperty(required=True)
	current_boat = ndb.StringProperty()
	arrival_data = ndb.DateTimeProperty()
	departure_history = ndb.DateTimeProperty(repeated=True)



####################
class BoatHandler(webapp2.RequestHandler):
	route = '/marina/boat/'

	def create(self):
		p_key = ndb.Key(Boat, "p_boat")
		data = json.loads(self.request.body)		
		boat = Boat(name=data['name'],
					b_type=data['type'],
					length=data['length'],
					atsea = True,
					parent=p_key
					)
		boat.put()
		b_dict = boat.to_dict()
		b_dict['id'] = boat.key.urlsafe()
		return b_dict


	def post(self):
		try:
			boat = self.create()
			self.response.set_status(201)
			self.response.write(boat)
		except:
			self.response.set_status(400)
			self.response.write("Failed to add boat")



	def get(self, id=None):
		if id:
			try:
				boat = ndb.Key(urlsafe=id).get()
				b_dict = boat.to_dict()
				b_dict['id'] = id
				self.response.write(json.dumps(b_dict))
			except:
				self.response.set_status(400)
				self.response.write("ID does not exsist")
		else:
			for b in Boat.query():
				b_d = b.to_dict()
				b_d['id'] = self.route+b.key.urlsafe() 
				self.response.write("\n"+json.dumps(b_d)+"\n")		


	def put(self, id=None):
		if not id:
			self.response.set_status(400)
			self.response.write("Missing ID")
			return
		
		id = id.split('/')
		if id[0]:
			if(id[1] == "at_sea"):
				self.set_atsea(id[0])
			elif(id[1] == "arrive"):
				self.set_arrival(id[0])
			else:
				self.response.set_status(400)
				self.response.write("Incorrect URL")
				return

	
	def set_atsea(self, id):
		try:
			b_key = ndb.Key(urlsafe=id)
			boat = b_key.get()
			if boat.atsea:
				self.response.set_status(403)
				self.response.write("Boat already at_sea")
				return
			else:
				boat.atsea = True
				boat.put()
				self.remove_from_slip(id)
				self.response.write("Boat removed from slip and set at_sea")
				 #need to remove from slip or give error is already at sea
		except:
			self.response.set_status(400)
			self.response.write("ID does not exsist")


	
	def set_arrival(self, id):
		#try:
			b_key = ndb.Key(urlsafe=id)
			boat = b_key.get()
			if boat.atsea:
				if self.add_to_slip(id):
					boat.atsea = False
					boat.put()
					self.response.set_status(201)
					self.response.write("Boat arrived at an open slip")
				else:
					self.response.set_status(403)
					self.response.write("All slips occupied. Can't arrive boat")
			else:
				self.response.set_status(403)
				self.response.write("Boat already in a slip")
		#except:
		#	self.response.set_status(400)
			#lf.response.write("ID does not exsist")
		# need to add to slip now or give error if already in slip


	def remove_from_slip(self, id):
		slips = Slip.query()
		self.response.write(id)
		for s in slips:
			if(s.current_boat == id):
				s.current_boat = None
				#log date
				s.put()
				return 


	def add_to_slip(self, id):
		slips = Slip.query()
		for s in slips:
			if(s.current_boat == None):
				#log data
				s.current_boat = self.route+id
				s.put()
				return True
		return False



	

	def delete(self, id=None):
		if not id:
			self.response.set_status(400)
			self.response.write("Missing ID")
			return
		
		try:
			b_key = ndb.Key(urlsafe=id)
			boat = b_key.get()
			boat.key.delete()
			self.remove_from_slip(id)
			self.response.set_status(203)
			self.response.write("Boat deleted")
		except:
			self.response.set_status(400)
			self.response.write("ID does not exsist")





################
class SlipHandler(webapp2.RequestHandler):
	route = '/marina/slip/'

	def create(self):
		p_key = ndb.Key(Slip, "p_slip")
		data = json.loads(self.request.body)	
		slip = Slip(number=data['number'],
					parent=p_key
					)
		slip.put()
		s_dict = slip.to_dict()
		s_dict['id'] = self.route+slip.key.urlsafe()
		return s_dict


	def post(self):
		slip = self.create()
		self.response.write(json.dumps(slip))


	def get(self, id=None):
		if id:
			slip = ndb.Key(urlsafe=id).get()
			s_dict = slip.to_dict()
			s_dict['id'] = id
			self.response.write(s_dict)
		else:
			for s in Slip.query():
				s_d = s.to_dict()
				s_d['id'] = self.route+s.key.urlsafe() 
				self.response.write("\n"+str(s_d)+"\n")	


	def delete(self, id=None):
		if not id:
			self.response.set_status(400)
			self.response.write("Missing ID")
			return
		try:
			s_key = ndb.Key(urlsafe=id)
			slip = s_key.get()
			slip.key.delete()
			
			self.remove_boat_from_slip(id)
			self.response.set_status(203)
			self.response.write("Slip deleted")
		except:
			self.response.set_status(400)
			self.response.write("ID does not exsist")


		def remove_boat_from_slip(self, id):
			pass





###################
class Main(webapp2.RequestHandler):
    def get(self):
        self.response.write('Welcome to the Marina!')


def allow_patch():
	allowed_methods = webapp2.WSGIApplication.allowed_methods
	new_allowed_methods = allowed_methods.union(('PATCH',))
	webapp2.WSGIApplication.allowed_methods = new_allowed_methods
allow_patch()

app = webapp2.WSGIApplication([
	('/marina', Main),
    ('/marina/boat', BoatHandler),
    ('/marina/boat/', BoatHandler),
    ('/marina/boat/(.*)', BoatHandler),
    ('/marina/slip', SlipHandler),
    ('/marina/slip/', SlipHandler),
    ('/marina/slip/(.*)', SlipHandler)
], debug=True)






# class Fish(ndb.Model):
#     name = ndb.StringProperty(required=True)
#     ph_min = ndb.IntegerProperty()




# class FishHandler(webapp2.RequestHandler):
# 	def post(self):
# 		parent_key = ndb.Key(Fish, "parent_fish")


# 		fish_data = json.loads(self.request.body)
# 		#self.response.write(json.dumps(fish_data)) #check data

# 		#make a fish
# 		new_fish = Fish(name=fish_data['name'], parent=parent_key)
# 		new_fish.put()

# 		# add key to fish
# 		fish_dict = new_fish.to_dict()
# 		fish_dict['self'] = '/fish/' + new_fish.key.urlsafe()
		
# 		self.response.write(json.dumps(fish_dict)) #check data



# 	def get(self, id=None):
# 		if id:
# 			fish = ndb.Key(urlsafe=id).get()
# 			fish_dict = fish.to_dict()
# 			fish_dict['self'] = '/fish/' + id
# 			self.response.write(json.dumps(fish_dict))