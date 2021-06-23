#!/usr/bin/python3

# Version 1.0
# par Fortinet
# Jan 2021

import os
import requests
import getopt
import argparse
import simplejson as json
from base64 import b64encode, b64decode
import urllib3
import sys
import gzip
import subprocess
import urllib.request
import validators
from fake_useragent import UserAgent
import locale
from bs4 import BeautifulSoup
import requests


host = "IP"
AI_api_key = "API_KEY"

# Please be careful when regenerate api token. Once new token has been generated, old one will be invalid.


class FAIApiClient_file():

	def __init__(self, url):
		self.url = 'https://' + url + '/api/v1/files?access_token=' + AI_api_key
		self.body = {"file_name": "",
			     "file_content": "",
			     "password": ""}

	def _handle_post(self, data):
		"""
		POST JSON request..

		@type data: dict
		@param data: JSON request data.
		@rtype: HttpResponse
		@return: JSON response data.
		"""
		response = requests.post(self.url, data=json.dumps(data), verify=False)

		return response

	def _load_file_for_upload(self, path_to_file, test_input, filename=''):
		"""
		Load file contents into input mapping.

		@type path_to_file: basestring
		@param path_to_file: files absolute path.
		@type test_input: dict
		@param test_input: JSON request data.
		@type filename: basestring
		@param filename: filename override optional param.
		@rtype: dict
		@return: updated JSON request dict.
		"""
		with open(path_to_file, 'rb') as f:
			data = f.read()
		filename = os.path.basename(path_to_file) if not filename else filename
		test_input['file_name'] = b64encode(filename.encode('utf-8'))
		test_input['file_content'] = b64encode(data)
		test_input['password'] = "1"
		return test_input

	def send_file(self, OVERRIDE_FILE = '../Resources/samples.zip'):
		# NOTE: 'OVERRIDE_FILE' should be the absolute path to the file.
		#       When submitting a file via API the noted file ('OVERRIDE_FILE')
		#       will be used as an OVERRIDE.
		test_input = self.body
		test_input = self._load_file_for_upload(OVERRIDE_FILE, test_input)
		response = self._handle_post(test_input)
		return response

	def _load_memory_for_upload(self, text_data, test_input, filename=''):
		"""
		Load file contents into input mapping.

		@type path_to_file: basestring
		@param path_to_file: files absolute path.
		@type test_input: dict
		@param test_input: JSON request data.
		@type filename: basestring
		@param filename: filename override optional param.
		@rtype: dict
		@return: updated JSON request dict.
		"""
		
		tmp_str = ""  

		data = b64encode(text_data)

		test_input['file_name'] = b64encode(filename.encode('utf-8'))
		test_input['file_content'] = data
		test_input['password'] = "1"
		return test_input

	def send_url(self, url_page,filename):
		# NOTE: 'OVERRIDE_FILE' should be the absolute path to the file.
		#       When submitting a file via API the noted file ('OVERRIDE_FILE')
		#       will be used as an OVERRIDE.
		test_input = self.body
		test_input = self._load_memory_for_upload(url_page, test_input,filename)
		response = self._handle_post(test_input)
		return response
		
def crawl(url,depth):

	count = 3  # amount of urls in each level
	url_list_depth = [[] for i in range(0, depth + 1)]
	url_list_depth[0].append(url)
	for depth_i in range(0, depth):
		for links in url_list_depth[depth_i]:
			valid = True
			try:
				response = requests.get(links,verify=False)
				
			except (requests.exceptions.InvalidSchema,requests.exceptions.MissingSchema,requests.exceptions.SSLError) as e:
				valid = False
				
			if (valid):
				soup = BeautifulSoup(response.text, 'html.parser')
				tags = soup.find_all('a')
				for link in tags:
					url_new = link.get('href')
					flag = False
					for item in url_list_depth:
						for l in item:
							if url_new == l:
								flag = True

					if url_new is not None and "http" in url_new and flag is False:
						url_list_depth[depth_i + 1].append(url_new)
						#print(links, "->", url_new)

			else:
				parse_url (links)


	return (url_list_depth)
	
def load_file_for_upload(path_to_file):
	
	with open(path_to_file, 'rb') as f:
		data = f.read()

	return gzip.compress(data)

def check_file_id(host, file_id):
	data = ""
	results_output	= ""

	tmp_url = "https://" + str(host) + "/api/v1/verdict?access_token=" + str(AI_api_key) + "&fileid=" + str(file_id)
	command= "curl -k -X GET \""+ tmp_url  + "\"  -H \"Content-Type: application/json\" "
	
	try:
		results_output = subprocess.check_output(command, shell=True)
		data =  json.loads(results_output)
		
	except subprocess.CalledProcessError as e:

		print(e)
		sys.exit(0)

	return (data)

def check_submission_results (submit_id,filename):
	data = ""
	results_output	= ""

	tmp_url = "https://" + str(host) + "/api/v1/verdict?access_token=" + str(AI_api_key) + "&sid=" + str(submit_id)
	command= "curl -k -X GET \""+ tmp_url  + "\"  -H \"Content-Type: application/json\" "
	
	try:
		results_output = subprocess.check_output(command, shell=True)
		data =  json.loads(results_output)

		if (len(data) > 0):
			for key in data:
				if (key == "results"):
					tmp_data = data[key]
					for key, value in tmp_data.items():
						if (key == "fileids"):
							if (len(value) > 0):
								for i in range(0,len(value)):
									file_id = value[i]
									new_data  = "DATA_IN_PROCESS"
									stop = True
									i = 1
									while stop:
										new_data = check_file_id(host, file_id)
										tmp_check = str(new_data)
										i = i + 1
										
										if (not ("DATA_IN_PROCESS" in tmp_check)):
											stop = False
										elif (i == 50 ):
											stop = False
											break

									
									results_metadata = "filename:" + str(filename)
									if (len(new_data) > 0):
										for key in data:
											if (key == "results"):
												try:
													tmp_data = new_data[key]
													for key, value in tmp_data.items():
														results_metadata = results_metadata + "," + str(key) + ":" + str(value)
												except KeyError as e:
													next
													
									print (results_metadata)

							else:
								print ("filename:" + str(filename)  + ",NO RESULTS")		
	except subprocess.CalledProcessError as e:

		sys.exit(0)

def parse_url (tmp_url):

	client = FAIApiClient_file(host)

	if (validators.url(tmp_url)):
		ua = UserAgent()
		the_page = ""
		
		try:
			request = urllib.request.Request(tmp_url, data=None, headers={'User-Agent':  str(ua)})
			response = urllib.request.urlopen(request)

			with urllib.request.urlopen(request) as response:
				try:
					the_page = response.read()

				except Exception  as e:
					pass
					
		except (urllib.error.URLError,urllib.error.ContentTooShortError,urllib.error.HTTPError) as e:
				print ("CANNOT GET  URL:"  + str(tmp_url))		
				sys.exit(0)

		if (len(the_page) > 1):
			filename = tmp_url.replace(",","_")
			tmp_data = json.loads(client.send_url(the_page,"url").text)
			if ("submit_id" in tmp_data):
				submit_id = tmp_data['submit_id']
				if (submit_id > 0) :
					filename = tmp_url.replace(",","_")
					check_submission_results (submit_id,filename)
				else:
					print ("url:" + str(tmp_url) , "NO RESULTS")		
		else:
			print ("url:" + str(tmp_url) , "NO RESULTS")		

	else:
		the_page = str.encode(tmp_url)
		if (len(the_page) > 1):
			filename = tmp_url.replace(",","_")
			tmp_data = json.loads(client.send_url(the_page,"url").text)
			if ("submit_id" in tmp_data):
				submit_id = tmp_data['submit_id']
				if (submit_id > 0) :
					filename = tmp_url.replace(",","_")
					check_submission_results (submit_id,"url")
				else:
					print ("url:" + str(tmp_url) , "NO RESULTS")		
		else:
			print ("url:" + str(tmp_url) , "NO RESULTS")		


def getpreferredencoding(do_setlocale = True):
	return "utf-8"

def main(argv):
	locale.getpreferredencoding = getpreferredencoding

	urllib3.disable_warnings()

	parser = argparse.ArgumentParser(description='Test upload files to FortiAi and fortisandbox tool')

	parser.add_argument("-f","--file",   type=str, help="Filename to submit")
	parser.add_argument("-u","--url",   type=str, help="Filename to submit")
	parser.add_argument("-d","--depth",  type=int, help="Depth for url analysis, default 0 (just the url page), if depth not defined, maxdepth 3")

	args = parser.parse_args()

	if ( not (args.file or args.url)):
		parser.print_help()
		sys.exit(0)

	if (args.depth):
		depth = args.depth
	else:
		depth = 0
		
	if (depth > 3):
		depth = 3
	
	if (args.file):
		client = FAIApiClient_file(host)
		tmp_data = json.loads(client.send_file(args.file).text)
		if ("submit_id" in tmp_data):
			submit_id = tmp_data['submit_id']
			if (submit_id > 0) :
				check_submission_results (submit_id,args.file)
			else:
				print ("filename:" + str(args.file) , "NO RESULTS")		

	if (args.url):

		if (depth == 0):

			parse_url (args.url)
		else:
		
			list_of_url_to_parse = ""
			list_url = crawl (args.url,depth)

			for i in list_url:
				tmp_list = i
				for j in tmp_list:
					parse_url(j)


# Example command: python FAI_Client.py <fai_ip> <api key> <sample file path>
if __name__ == '__main__':
    main(sys.argv)

