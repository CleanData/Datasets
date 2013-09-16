#!/Library/Frameworks/EPD64.framework/Versions/Current/bin/python
# -*- coding: utf-8 -*-

import urllib2
from urllib2 import urlopen
import sys, os
from string import *
import json
import re
import datetime
import json
from urls import all_urls
import pickle

existing_licenses=["Public Domain Dedication and License (PDDL)","Open Data Commons Attribution License (ODC-By)","Open Data Commons Open Database License (ODC-ODbL)","CC0","public domain","GNU General Public License (GPL)","MIT","Apache 2.0","BSD 3-Clause License","BSD 2-Clause License","GNU Lesser Public License v3.0","Mozilla Public License v2.0","Common Development and Distribution License 1.0","Eclipse Public License","Unknown","Copyright"]

# get all the URLs
def getAllURLs():

	urls=[]
	# It looks like there's around 10 pages of apps on BigApps
	for i in range(0,10):

		# create a request, and make it a proper user agent to avoid 403 errors
		request=urllib2.Request("http://nycbigapps.com/project?offset={:.0f}".format(i*20))
		request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
		text=urlopen(request).read()
		
		# split on the HELP BUILD element to create an array of the app listings
		blocks=text.split("<h4 style=\"margin-top: 0px;\"><strong>HELP BUILD</strong></h4>")
		for j in range(1,len(blocks)):
			# for each block, use the DOM strings to pull out the urls
			chunk=blocks[j].split("class=\"red\"")[0].split("href=")[1]

			# strip the quotes and white space
			link=replace(chunk,"\"","").strip()
			
			# now that we have the url, add it to a list
			urls.append(link)

	# print to std out, but also save to a pickle file (small, compressed python format)
	print urls
	
	# create the file to write out to
	fout=open("urls.pkl",'w')
	# dump the data
	pickle.dump(urls,fout)
	# close the file again
	fout.close()

# for each url, strip out the relevant information to create the dataset objects, and the relations
def getDatasetMap(url):
	# Data Structure
	"""
	{
		"model":"data_connections.Dataset",
		"pk":null,
		"fields":{
            "description": "",
            "license": ["MIT"],
            "date_last_edited": "2013-07-27T01:31:13Z",
            "url": "http://example.com/",
            "data_format": ["JSON"],
            "date_published": "2013-07-27T01:31:11Z",
            "manager": null,
            "managing_organization": null,
            "data_catalog": null,
            "name": "Test dataset"
		}
	}
	"""
	dataset={"model":"data_connections.Dataset","pk":None,"fields":{
		"description": "",
		"license": [],
		"date_last_edited": "",
		"url": "",
		"data_format": [],
		"date_published": "",
		"manager": None,
		"managing_organization": None,
		"data_catalog": None,
		"name": ""
	}}

	request=urllib2.Request(url)
	request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
	text=urlopen(request).read()

	dataset["fields"]["url"] = url
	dataset["fields"]["name"] = text.split("<strong>HELP BUILD</strong></h4> <h1 class=\"page_title red\">")[1]\
									.split("</h1>")[0].strip()
	# TODO - This should be made a lot safer. This is a security hole as it allows us to be adding
	# raw html into the database. We should add a check here to make the description
	# field safer.
	dataset["fields"]["description"] = text.split("<h2 class=\"toppend-1\">Project Description</h2>")[1]\
											.split("</h2>")[0]\
											.split("<h2 class=\"plain\">")[1].strip()
	dataset["fields"]["license"]=["Unknown"]

	# These are actually strings in the format %Y-%m-%dT%H:%M:%SZ so keep this in this format
	# it's a hack, but the deadline for bigapps 2013 was 5pm on the 7th of June
	dataset["fields"]["date_last_edited"]="2013-06-07T17:00:00Z"
	dataset["fields"]["date_published"]="2013-06-07T17:00:00Z"

	# These are foreign key relations - so they are a list of attributes rather than a value
	# see here to understand why: https://docs.djangoproject.com/en/1.5/topics/serialization/#natural-keys
	dataset["fields"]["data_format"]=["Application"]
	dataset["fields"]["license"]=["Unknown"]

	# get the relevant info for the manager foreign key
	manager=[]
	manager_name=text.split("http://nycbigapps.com/person/")[1].split("</a>")[0].split(">")[-1]
	first = manager_name.split(" ")[0].strip()
	rest = manager_name.split(first)[1].strip()

	profile_url = "http://nycbigapps.com/person/"+text.split("http://nycbigapps.com/person/")[1].split("\">")[0].strip()
	manager = [first,rest,profile_url]

	dataset["fields"]["manager"] = manager	
	dataset["fields"]["managing_organization"] = []
	organization = []
	
	# TODO: uncomment and build out this section
	"""
	data_relations = []
	datasets = something.split("on some string")
	for dataset in datasets:
		data_relation["source"]=["....."]
		data_relation["derivative"]=["....."]
		data_relation["how_data_was_processed"]=""
		data_relations.append(data_relation)

	if len(datasets)==0:
		return None
		# and remember to handle this return value!

	return dataset,manager,organization,license,data_relations
	"""
	
	return dataset,manager,organization,license

def getAllDataSets():
	datasets = []
	managers = []
	organizations = []
	licenses = []
	counter=0
	
	# read the urls in from the pickle file
	urls=pickle.load(open("urls.pkl"))
	for url in urls:
		counter+=1
		if counter%10==0:
			print "Done {} of {}".format(counter,len(urls))

		# ======================================================================
		# TODO - extend this to accomodate data_relations as well
		# TODO - This is the place that needs to handle the None output when the reading finds a
		# page that shouldn't be a separate object - like a page with no listed datasets
		dataset,manager,organization,license = getDatasetMap(url)

		if manager not in managers:
			managers.append(manager)
		if organization not in organizations:
			organizations.append(organization)
		if license not in licenses:
			licenses.append(license)
		datasets.append(dataset)

	# dump all of this to a local pickle file for safe keeping. Parsing to json happens next
	# by having these as two separate steps we minimize the amount of site scraping
	# which is just good practice for minimizing aggravation to other sites.
	pickle.dump({"datasets":datasets,"licenses":licenses,"organizations":organizations,"managers":managers},open("bigapps.pkl",'w'))
	
# This dumps the data into the individual json files that map onto the data structure for the site
def printJSONs(filename_in):
	data = pickle.load(open(filename_in))
	
	# print out the datasets json
	json.dump(data["datasets"],open("datasets.json",'w'),indent=4)
	
	orgs=[]
	print data["organizations"]
	for o in data["organizations"]:
		print o
		org={"model":"data_connections.Organization","pk":None,"fields":{"name":o,"url":""}}
		orgs.append(org)
	json.dump(orgs,open("organizations.json",'w'),indent=4)
	
	managers=[]
	for m in data["managers"]:
		sc={
				"model":"data_connections.Scientist",\
				"pk":None,\
				"fields":{
					"firstname":m[0],\
					"lastname":m[1],\
					"profile_url":m[2]
				}
			}
		managers.append(sc)		
	json.dump(managers,open("scientists.json",'w'),indent=4)

	new_licenses=[]
	for l in data["licenses"]:
		l_name=l
		if l_name=="Public":
			l_name="public domain"
		
		# highlight missing licenses
		# TODO - change this to a file that outputs a new file my_licenses.json
		if l_name not in existing_licenses:
			print l_name
			print l
	print "Done!"

# This is code that is run if the file is run as the main program - e.g. python scraper_bigapps.py
# This code won't be run if you include the code like a package - i.e. from scraper_bigapps include *
#
# at the moment, just comment out the lines that you don't want to run
if __name__=="__main__":
	# get a list of all the urls that contain applications
	getAllURLs()
	# run through the list of urls and parse each page to create a dataset object
	getAllDataSets()
	# print the outputs as jsons
	printJSONs(filename_in="bigapps.pkl")

