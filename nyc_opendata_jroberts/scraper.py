#!/Library/Frameworks/EPD64.framework/Versions/Current/bin/python
# -*- coding: utf-8 -*-

from urllib2 import urlopen
import sys, os
from string import *
import json
import re
from nyc_opendata_urls import all_urls
import datetime
import json

import pickle

existing_licenses=["Public Domain Dedication and License (PDDL)","Open Data Commons Attribution License (ODC-By)","Open Data Commons Open Database License (ODC-ODbL)","CC0","public domain","GNU General Public License (GPL)","MIT","Apache 2.0","BSD 3-Clause License","BSD 2-Clause License","GNU Lesser Public License v3.0","Mozilla Public License v2.0","Common Development and Distribution License 1.0","Eclipse Public License","Unknown","Copyright"]

def getAllURLs():
	urls=[]
	for i in range(1,85):
		print i
		text=urlopen("https://nycopendata.socrata.com/browse?limitTo=datasets&page={:.0f}".format(i)).read()
		blocks=text.split("<td class=\"nameDesc\">")
		for j in range(1,len(blocks)):
			chunk=blocks[j].split("class=\"name\"")[0].split("href=")[1]
			link=replace(chunk,"\"","").strip()
			print link
			urls.append(link)

	print urls

def getAllDataSets():
	datasets = []
	managers = []
	organizations = []
	licenses = []
	counter=0
	for url in all_urls:
		counter+=1
		if counter%10==0:
			print "Done {} of {}".format(counter,len(all_urls))
		dataset,manager,organization,license = getDatasetMap(url)

		if manager not in managers:
			managers.append(manager)
		if organization not in organizations:
			organizations.append(organization)
		if license not in licenses:
			licenses.append(license)
		datasets.append(dataset)

	pickle.dump({"datasets":datasets,"licenses":licenses,"organizations":organizations,"managers":managers},open("nyc_opendata.pkl",'w'))
	
def printJSONs(file_in):
	data = pickle.load(open(file_in))
	
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
		
		if l_name not in existing_licenses:
			print l_name
			print l
	print "Done!"

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

	text=urlopen(url+"/about").read()
	
	dataset["fields"]["url"] = url
	dataset["fields"]["name"] = text.split("id=\"datasetName\"")[1].split("</h2>")[0].split(">")[1].strip()
	dataset["fields"]["description"] = text.split("<div id=\"description\">")[1].split("<p class=\"collapsed\">")[1].split("</p>")[0].strip()
	license = text.split("<dt>Permissions</dt>")[1].split("<dd>")[1].split("</dd>")[0].strip()
	dataset["fields"]["license"]=[license]

	update_timestamp=int(text.split("class=\"aboutUpdateDate\">")[1].split("\">")[0].split("data-rawDateTime=\"")[1])
	dataset["fields"]["date_last_edited"]=datetime.datetime.fromtimestamp(update_timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

	pub_timestamp=int(text.split("class=\"aboutCreateDate\">")[1].split("\">")[0].split("data-rawDateTime=\"")[1])
	dataset["fields"]["date_published"]=datetime.datetime.fromtimestamp(update_timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

	dataset["data_format"]=["CSV"]

	manager=[]
	manager_name=text.split("class=\"aboutAuthorName\"")[1].split("</a>")[0].split(">")[-1]
	first = manager_name.split(" ")[0].strip()
	rest = manager_name.split(first)[1].strip()
	profile_url = "https://data.cityofnewyork.us"+text.split("class=\"aboutAuthorName\" href=\"")[1].split("\">")[0].strip()
	manager = [first,rest,profile_url]

	dataset["fields"]["manager"] = manager
	
	organization = text.split("<dt>Data Provided By</dt>")[1].split("</dd>")[0].split("<dd>")[1].strip()
	dataset["fields"]["managing_organization"] = [organization]
	
	return dataset,manager,organization,license

printJSONs("nyc_opendata.pkl")
#getAllDataSets()
sys.exit()	
