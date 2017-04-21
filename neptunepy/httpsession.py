# -*- coding: utf-8 -*-
# @Author: bryanthayes
# @Date:   2017-04-20 22:35:56
# @Last Modified by:   bryanthayes
# @Last Modified time: 2017-04-20 22:56:55
import sys, requests, json

# TODO(bhayes): Add support for PUT, DELETE, UPDATE requests
class HTTPSession(object):
	def __init__(self):
		self.session = requests.Session()

	def POST(self, root, path, data, headers=None):
		''' Issue a POST http web request given a path and data for args '''
		
		# Load headers if applicable
		if (headers == None):
			headers = {"content-type" : "application/json"}
		else:
			headers = headers

		try:
			url = root + path
			result = self.session.post(url, data=data, headers=headers).json()
			return result
		except requests.exceptions.RequestException as e:
			print("ERROR: {}".format(e))
			raise

	def GET(self, root, path, data):
		''' Issue a GET http web request given a path and data payload '''
		try:
			url = root + path
			result = self.session.get(url, data).json()
			return result
		except requests.exceptions.RequestException as e:
			print("ERROR: {}".format(e))
			raise

def main():
	''' Test code '''
	# Get instance of manager
	session = HTTPManager()

	# issue a test POST request
	rv = session.POST("http://httpbin.org", "/post", {})
	if rv != None:
		print(rv)

	# issue a test GET request
	rv = session.GET("http://httpbin.org", "/get", {})
	if rv != None:
		print(rv)

if __name__ == "__main__":
	main()