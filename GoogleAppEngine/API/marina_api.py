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
			self.response.write(json.dumps(boat))
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
				self.response.write("ID does not exist")
		else:
			for b in Boat.query():
				b_d = b.to_dict()
				b_d['id'] = self.route+b.key.urlsafe() 
				self.response.write(json.dumps(b_d))		



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
		except:
			self.response.set_status(400)
			self.response.write("ID does not exist")


	
	def set_arrival(self, id):
		try:
			b_key = ndb.Key(urlsafe=id)
			boat = b_key.get()
			if boat.atsea:
				if self.add_to_slip(id):
					boat.atsea = False
					boat.put()
					self.response.set_status(200)
					self.response.write("Boat arrived at an open slip")
				else:
					self.response.set_status(403)
					self.response.write("All slips occupied. Can't arrive boat")
			else:
				self.response.set_status(403)
				self.response.write("Boat already in a slip")
		except:
			self.response.set_status(400)
			self.response.write("ID does not exsist")



	def remove_from_slip(self, id):
		slips = Slip.query()
		for s in slips:
			if(s.current_boat == self.route+id):
				s.current_boat = None
				s.put()
				return 



	def add_to_slip(self, id):
		slips = Slip.query()
		for s in slips:
			if(s.current_boat == None):
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
			self.response.write("ID does not exist")


	def patch(self, id=None):
		if not id:
			self.response.set_status(400)
			self.response.write("Missing ID")
			return

		try:
			data = json.loads(self.request.body)
			try:
				b_key = ndb.Key(urlsafe=id)
				boat = b_key.get()
				try:
					if data['name']:
						boat.name = data['name']
						boat.put()
				except: pass
				try:
					if data['type']:
						boat.b_type = data['type']
						boat.put()
				except: pass
				try:
					if data['length']:
						boat.length = data['length']
						boat.put()
				except:
					self.response.set_status(400)
					self.response.write("Length must be an integer")
					return
				
				boat = ndb.Key(urlsafe=id).get()
				b_dict = boat.to_dict()
				b_dict['id'] = self.route+id
				self.response.set_status(202)
				self.response.write(json.dumps(b_dict))
			except:
				self.response.set_status(400)
				self.response.write("ID does not exist")
		except:
			self.response.set_status(400)
			self.response.write("Missing raw json")






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
		s_dict['id'] = slip.key.urlsafe()
		return s_dict


	def post(self):
		try:
			slip = self.create()
			self.response.set_status(201)
			self.response.write(json.dumps(slip))
		except:
			self.response.set_status(400)
			self.response.write("Failed to add slip")


	def get(self, id=None):
		if id:
			slip = ndb.Key(urlsafe=id).get()
			s_dict = slip.to_dict()
			s_dict['id'] = id
			self.response.write(json.dumps(s_dict))
		else:
			for s in Slip.query():
				s_d = s.to_dict()
				s_d['id'] = self.route+s.key.urlsafe() 
				self.response.write(json.dumps(str(s_d)))	


	def delete(self, id=None):
		if not id:
			self.response.set_status(400)
			self.response.write("Missing ID")
			return
		try:
			s_key = ndb.Key(urlsafe=id)
			slip = s_key.get()
			slip.key.delete()
			if not (slip.current_boat == None):
				boat_id = slip.current_boat
				self.remove_boat_from_slip(boat_id.split("/")[3])
			self.response.set_status(203)
			self.response.write("Slip deleted")
		except:
			self.response.set_status(400)
			self.response.write("ID does not exsist")


	def remove_boat_from_slip(self, id):
		b_key = ndb.Key(urlsafe=id)
		boat = b_key.get()
		boat.atsea = True
		boat.put()




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


