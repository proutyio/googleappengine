from __future__ import print_function
import sys
from flask import Flask, render_template, request, redirect, session
from google.appengine.api import urlfetch
import urllib
# from webapp2_extras import sessions
# from webapp2 import redirect
import json


app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route("/startflow/", methods=['GET'])
def startflow():
	url = url_get_oauth()
	return redirect(url)


def url_get_oauth():
	url = "https://accounts.google.com/o/oauth2/v2/auth?"
	code = "response_type=code"
	c_id = "&client_id=1073799262782-1glid3shm3a3jgrfn54inafn9qln40pa.apps.googleusercontent.com"
	redirect = "&redirect_uri=http://localhost:8080/oauth2callback"
	scope = "&scope=email"
	state = "&state=secret"
	return url+code+c_id+redirect+scope+state



@app.route('/oauth2callback', methods=['GET', 'POST'])
def callback():
	#print(request.args['code'], file=sys.stderr)
	if request.methods == 'GET':
		code = request.args['code']
		data = urllib.urlencode( post_token_data(code) )
		headers = {'Content-Type': 'application/x-www-form-urlencoded'}
		result = urlfetch.fetch(url='https://www.googleapis.com/oauth2/v4/token',
								payload=data,
								method=urlfetch.POST,
								headers=headers)
		session['token'] = result
		print(result.content, file=sys.stderr)

	if request.method == 'POST':
		return request.content



def post_token_data(oauth_code):
	data = {'code':oauth_code,
			'client_id':'1073799262782-1glid3shm3a3jgrfn54inafn9qln40pa.apps.googleusercontent.com',
			'client_secret':'NwTKpmx_SZnZP-FyZHnVH2Md',
			'redirect_uri':'http://localhost:8080/oauth2callback',
			'grant_type':'authorization_code'}
	return data


