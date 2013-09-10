#!/usr/bin/python

import urllib
import urllib2
import re
import json
from time import sleep


# datahub.io/robots.txt
CrawlDelay = 11
Disallow = ["/dataset/rate/","/revision/","/dataset/*/history","/api/"]
spider_name = "Python-urllib/2.7 CleanData_OpenDataResearch"
headers = { 'User-Agent' : spider_name }


#if url contains http, use urllib2 request, 
#after each request, sleep for CrawlDelay number of seconds 
# read the file name or url, sleeps for a few seconds and return the result
def read_url(url, delay=10, values={}): #read url and return the content
    is_url = re.compile("http")
    if is_url.match(url) :
        if len(values) == 0:
            req = urllib2.Request(url.strip(), headers= headers)
        else:
            data = urllib.urlencode(values)
            req = urllib2.Request(url.strip(), data.encode("utf-8"), headers)
        try: 
            response = urllib2.urlopen(req)
            sleep(CrawlDelay)
        except urllib2.HTTPError as e :
            print("read_url openurl, reason: ", e.reason) 
            print("HTTP Error code: ",e.code)
        except urllib2.URLError as e :
            print("read_url openurl, reason: ", e.reason) 
        else:
            return response.read()
    else:
        try:
            f = open(url.strip())
            sleep(delay)
        except IOError as e:
            print("read_url file open, reason: ", e)
        else:
            return f.read()
    return ""

# remove blank lines    
def remove_newline(orig_str):
    tempstr = orig_str.strip()   
    tempstr = tempstr.replace('\r\n',' ')      
    tempstr = tempstr.replace('\r',' ')
    tempstr = tempstr.replace('\n',' ')
    return tempstr
    
##########################################################################################

# http://docs.ckan.org/en/ckan-2.0.2/ckan.logic.action.get.html
#
# ckan_action_get = '/api/3/action/'
# package_list_path = ckan_action_get + 'package_list'
# package_show_path = ckan_action_get + 'package_show?id='
# license_list_path = ckan_action_get + 'licence_list'
# tag_list_path = ckan_action_get + 'tag_list'
# related_list_path = ckan_action_get + 'related_list?id='



# returns crawler_delay 
def robots_txt(site_root):
    robots_txt = read_url(site_root + 'robots.txt')
    if len(robots_txt) > 0 :
        temp = re.findall(r'Crawl-Delay:\s*([0-9]+)',robots_txt)    
        if len(temp) > 0 :
            return (int(temp[0]) +1 )
    return 10


    


# http://docs.ckan.org/en/ckan-2.0.2/api.html
# read the licenses used on a ckan site, returns a list of license dictionaries
# site_root : the domain name of the ckan site
# delay : crawler-delay defined in robots.txt
# returns a list of license dictionaries, return an empty list if read fails
def license_list(site_root, delay=10):
    pagejson = read_url(site_root + '/api/3/action/licence_list' , delay = delay)
    if len(pagejson) > 0:
        temp = json.loads(pagejson)
        if temp['success']: 
            license_list = temp["result"]
            return license_list
    return []
    
# create a license list in the format of licenses.json from the ckan license dictionaries
#  {
#		#"model":"data_connections.License", //will be added later when writing to my_licenses.json 
#		#"pk":1, //will be added later when writing to my_licenses.json 
#		"fields":{
#			"name":"Public Domain Dedication and License (PDDL)",
#			"url":"http://opendatacommons.org/licenses/pddl/"
#		}
#	}
def license_convert(ckan_license_list):
    license_list = []
    if len(ckan_license_list) > 0:
        for ckan_license in ckan_license_list:
            a_license = { 'fields':{} }
            a_license['fields']['name'] = ckan_license['title'] 
            a_license['fields']['url'] = ckan_license['url']
            license_list.append(a_license)
    return license_list

# write my_licenses.json 
def my_licenses(license_list, core_license_path, my_license_path):
    try:
        f = open(core_license_path)
        core_license_file = f.read()
        f.close()
        core_license_list = json.loads(core_license_file)
        #[{'url':item['fields']['url'], 'name':item['fields']['name']} for item in l ]
        core_pairs = [{'name':item['fields']['name'], 'url':item['fields']['url']} for item in core_license_list ] 
        my_license_list = []
        i = 0
        for item in license_list :
            test_item = {'name':item['fields']['name'], 'url':item['fields']['url']}
            if not test_item in core_pairs :
                my_license_list.append({})
                my_license_list[i]['fields'] = test_item          
                my_license_list[i]['model'] = "data_connections.License"
                my_license_list[i]['pk'] = i+1
                i = i+1
        f = open(my_license_path,'w')
        f.write(json.dumps(my_license_list, indent=4))
        f.close()
    except IOError as e:
        print("my_licenses file open, reason: ", e)
        return [] 
    else:        
        return my_license_list

############################################################################################

# http://docs.ckan.org/en/ckan-2.0.2/api.html    
# read the dataset(package) identifiers from a ckan site and return a list 
# site_root : the domain name of the ckan site
# delay : crawler-delay defined in robots.txt
# returns a list of package identifiers, return an empty list if read fails
def package_list(site_root, delay=10):
    pagejson = read_url(site_root + '/api/3/action/package_list' , delay)
    if len(pagejson) > 0:
        temp = json.loads(pagejson)
        if temp['success']: 
            package_list = temp["result"]
            return package_list
    return []

# http://docs.ckan.org/en/ckan-2.0.2/api.html          
# read dataset(package) information from a ckan site and return the package object
# site_root : the domain name of the ckan site
# package_name : the identifier of the dataset
# delay : crawler-delay defined in robots.txt
# returns a dictionary of the package data, returns an empty dictionary if read fails
def package_show(site_root, package_name, delay=10):
    pagejson = read_url(site_root + '/api/3/action/package_show?id=' + package_name, delay)
    if len(pagejson) > 0:
        temp = json.loads(pagejson)
        if temp['success']: 
            curr_package = temp["result"]
            return curr_package
    return {}
    
    
