# Kyle Prouty
# Winter 2018
# CS 496
from __future__ import print_function
from flask import Flask, session, render_template, request, redirect, g
from google.appengine.api import urlfetch
import urllib
import uuid
import sys
import json

app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route("/startflow/", methods=['GET'])
def startflow():
	state = random_state()
	url = url_start_oauth(state)
	return redirect(url)


def url_start_oauth(random_state):
	url = "https://accounts.google.com/o/oauth2/v2/auth?"
	code = "response_type=code"
	c_id = "&client_id=1073799262782-1glid3shm3a3jgrfn54inafn9qln40pa.apps.googleusercontent.com"
	redirect = "&redirect_uri=https://clouddev-194405.appspot.com/oauth2callback"
	#redirect = "&redirect_uri=http://localhost:8080/oauth2callback"
	scope = "&scope=email"
	state = "&state="+random_state
	return url+code+c_id+redirect+scope+state



def random_state():
	state = uuid.uuid4()
	return str(state).replace("-","") 



@app.route('/oauth2callback', methods=['GET', 'POST'])
def callback():
	state = request.args['state']
	code = request.args['code']
	post_result = post_return_token(code)	
	user_data = get_user_data(post_result['access_token'])
	return render_template('userpage.html', user_data=user_data, state=state, token=post_result['access_token'])



def post_return_token(oauth_code):
	payload = {'code':oauth_code,
			'client_id':'1073799262782-1glid3shm3a3jgrfn54inafn9qln40pa.apps.googleusercontent.com',
			'client_secret':'NwTKpmx_SZnZP-FyZHnVH2Md',
			#'redirect_uri':'http://localhost:8080/oauth2callback',
			'redirect_uri':'https://clouddev-194405.appspot.com/oauth2callback',
			'grant_type':'authorization_code'}
	data = urllib.urlencode(payload)
	headers = {'Content-Type': 'application/x-www-form-urlencoded'}
	result = urlfetch.fetch(url='https://www.googleapis.com/oauth2/v4/token',
							payload=data,
							method=urlfetch.POST,
							headers=headers)
	return json.loads(result.content)



def get_user_data(token):
	headers = {'Authorization':"Bearer "+token}
	result = urlfetch.fetch(url='https://www.googleapis.com/plus/v1/people/me',
								method=urlfetch.GET,
								headers=headers)
	return json.loads(result.content)