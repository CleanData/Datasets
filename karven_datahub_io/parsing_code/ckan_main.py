#!/usr/bin/python


from shared_functions import read_url    
from shared_functions import remove_newline 
from shared_functions import robots_txt         
from shared_functions import license_list  
from shared_functions import license_convert
from shared_functions import my_licenses
from shared_functions import package_list 
from shared_functions import package_show    
from spam_filter import add_spam_score
from operator import itemgetter, attrgetter
import datetime
import re          
from time import sleep      
import sys
import json
                      
data_root = '../data/'
default_datasets_path = data_root + 'datasets.json'
default_my_licenses_path = data_root + 'my_licenses.json'
default_formats_path = data_root + 'my_formats.json'
default_datacatalogs_path = data_root + 'datacatalogs.json'
default_datarelations_path = data_root + 'datarelations.json'
default_organizations_path = data_root + 'organizations.json'
default_scientists_path = data_root + 'scientists.json'

#core_licenses_path = '../../example_dataset/licenses.json'
core_licenses_path = 'licenses.json'
core_formats_path = 'formats.json'

#
def ckan_spider(site_root = 'http://datahub.io/', datasets_path=default_datasets_path,
                my_licenses_path=default_my_licenses_path, formats_path=default_formats_path,
                datacatalogs_path=default_datacatalogs_path, datarelations_path=default_datarelations_path,
                organizations_path=default_organizations_path, scientists_path=default_scientists_path ): 
    # test robots.txt
    # test licenses read, write
    # test datasets read, write
    # datacatalogs, scientists and organizations
    # test formats
    print("running spider")
    delay = robots_txt(site_root)
    
    ckan_licenses = license_convert(license_list(site_root,10))
    mylicenses = my_licenses(ckan_licenses, core_license_path, my_license_path)
    

def ckan_test_robots(site_root) :
    print('ckan_test_robots Crawl-delay: ' + str(robots_txt(site_root)))    

def ckan_test_licenses(site_root, core_license_path, my_license_path) :    
    ckan_licenses = license_convert(license_list(site_root,10))
    f = open('ckan_licenses.json','w')
    f.write(json.dumps(ckan_licenses,indent=4))
    f.close()
    f = open('ckan_licenses.json')
    ckan_licenses = json.loads(f.read())  
    f.close()  
    mylicenses = my_licenses(ckan_licenses, core_license_path, my_license_path)
    print(mylicenses) 

def ckan_test_package_list(site_root, delay) :
    ckan_package_list = package_list(site_root, delay)
    f = open('ckan_package_list.json','w')
    f.write(json.dumps(ckan_package_list,indent=4))
    f.close()

def ckan_test_package_read(site_root, package_file_path, output_file_path, delay) :
    f = open(package_file_path)
    package_list = json.loads(f.read())
    f.close()
    out = []
    for package_name in package_list :
        out.append(package_show(site_root, package_name, delay))    
        output = open(output_file_path,'w')                     
        output.write(json.dumps(out, indent=4))        
        output.close()  
        print(str(len(out)) + " " + package_name)    

def ckan_test_spam_score(ckan_datasets_path, output_file_path) :
    f = open(ckan_datasets_path)
    ckan_package_list = json.loads(f.read())
    f.close()
    for i in range(len(ckan_package_list)) :
        spam_score = add_spam_score(ckan_package_list[i])
        ckan_package_list[i]['spam_score'] = spam_score
    print(ckan_package_list[0]['spam_score']) 
    sorted_package_list = sorted(ckan_package_list, key=itemgetter('spam_score'), reverse=True)
    output = open(output_file_path,'w')                     
    output.write(json.dumps(sorted_package_list, indent=4))        
    output.close()  
    

def ckan_test_convert_package(ckan_datasets_path, max_spam_score = 3000, datasets_path=default_datasets_path,
                my_licenses_path=default_my_licenses_path, formats_path=default_formats_path,
                datacatalogs_path=default_datacatalogs_path, datarelations_path=default_datarelations_path,
                organizations_path=default_organizations_path, scientists_path=default_scientists_path ):    
    f = open(ckan_datasets_path)
    ckan_package_list = json.loads(f.read())
    f.close()             
    datacatalogs = []
    datasets = []
    formats = []
    organizations = []
    scientists = []
    for x in ckan_package_list :
        print(x['name'])                                  
        if 'spam_score' in x and x['spam_score'] >= max_spam_score : 
            continue                                      
        if x['num_resources'] > 1 :
            #datacataglog
          	#{
            #		"model":"data_connections.DataCatalog",
            #		"pk":null,
            #		"fields":{
            #			"name":"2010 US Census",
            #			"manager":null,
            #			"managing_organization":["U.S. Census Bureau"]
            #     #"spam_score": , "datahub_name":
            #		}
            #}
            a_catalog = {"model":"data_connections.DataCatalog","pk":None,"fields":{} }
            a_catalog['fields']['name'] = x['title']
            if x['maintainer'] and len(x['maintainer']) > 0 :
                #HERE         
                a_manager =                    
            a_catalog['fields']['manager'] = x['maintainer']                              
            a_catalog['fields']['managing_organization'] = x['author']   
            #extra fields for datahub             
            a_catalog['fields']['datahub_name'] = x['name']              
            if 'spam_score' in x :                                                   
                a_catalog['fields']['spam_score'] = x['spam_score']
            datacatalogs.append(a_catalog)
            #organizations
            #{
            #    "model":"data_connections.Organization",
            #    "pk":null,
            #    "fields":{
            #    "name":"Mayor's Office of Long-Term Planning and Sustainability, NYC",
            #    "url":"http://www.nyc.gov/html/planyc2030/html/about/who-we-are.shtml"
            #    }
            #}                          
            if a_resource["author"] not in [ item['fields']['name'] for item in organizations ]  :   
                a_organization = { "model":"data_connections.Organization", "pk":None, 'fields':{} }
                a_organization['fields']['name'] = x["author"]              
                a_organization['fields']['url'] = ''
                formats.append(a_organization)
            #scientists
            #{
            #    "model":"data_connections.Scientist",
            #    "pk":null,
            #    "fields":{
            #    "firstname":"Albert",
            #    "lastname":"Webber",
            #    "profile_url":"https://data.cityofnewyork.us/profile/Albert-Webber/txun-eb7e"
            #    }
            #}
             
            for a_resource in x['resources'] :
                #datasets                                 
                #{
                # 		"model":"data_connections.Dataset",
                # 		"pk":null,
                #		  "fields":{
                #            "description": "",
                #            "license": ["MIT"],
                #            "date_last_edited": "2013-07-27T01:31:13Z",
                #            "url": "http://example.com/",
                #            "data_format": ["JSON"],
                #            "date_published": "2013-07-27T01:31:11Z",
                #            "manager": null,
                #            "managing_organization": null,
                #            "data_catalog": null,
                #            "name": "Test dataset"
                # 		}
                #	},
                a_dataset = {		"model":"data_connections.Dataset","pk":None,"fields":{}}                 
                a_dataset['fields']['description'] = unicode(a_resource['description']) +' ( ' + unicode(x['notes']) + ' ) '     
                a_dataset['fields']['license'] = [ x['license_title'] ]                         
                a_dataset['fields']['date_last_edited'] = a_resource["last_modified"]
                a_dataset['fields']['url'] = a_resource["url"]                
                if a_resource["format"] and len(a_resource["format"]) > 0 :                           
                    a_dataset['fields']['data_format'] = [ a_resource["format"] ]
                else :                                                                            
                    a_dataset['fields']['data_format'] = [ a_resource["mimetype"] ]                    
                a_dataset['fields']['date_published'] = a_resource["last_modified"]
                a_dataset['fields']['manager'] = x['maintainer']                              
                a_dataset['fields']['managing_organization'] = x['author']       
                a_dataset['fields']['data_catalog'] = [ x['title'] ]
                a_dataset['fields']['name'] = unicode(x['title']) + " " + unicode(a_resource['name']) + " " + unicode(a_resource['format']) # catalog.title + name + format       
                #extra fields for datahub             
                a_dataset['fields']['datahub_name'] = x['name']              
                if 'spam_score' in x :                                                   
                    a_dataset['fields']['spam_score'] = x['spam_score']
                datasets.append(a_dataset)
                #formats
                #{
                #    "model":"data_connections.Format",
                #    "pk":1,
                #    "fields":{
                #    "name":"JSON",
                #    "url":"http://en.wikipedia.org/wiki/JSON"
                #}
                if a_resource["format"] not in [ item['fields']['name'] for item in formats ]  :
                    a_format = { "model":"data_connections.Format", "pk":None, 'fields':{} }
                    a_format['fields']['name'] = a_resource["format"]              
                    a_format['fields']['url'] = ''
                    formats.append(a_format)
                
        elif x['num_resources'] == 1 :
            pass
            #datasets
        else :
            pass
            #spam 
        #write to datacatalogs.json   
        output = open(datacatalogs_path,'w')    
        output.write(json.dumps(datacatalogs, indent=4))     
        output.close()          
        #write to datasets.json, 
        output = open(datasets_path,'w')    
        output.write(json.dumps(datasets, indent=4))     
        output.close()  
        #write to organziations.json      
        output = open(organizations_path,'w')    
        output.write(json.dumps(organizations, indent=4))     
        output.close()  
        #check example formats to remove duplicates, assign primary keys, write to formats.json
        f = open(core_formats_path)
        core_formats = json.loads(f.read())
        core_format_names = [ item['fields']['name'] for item in core_formats ]
        f.close()
        my_formats = []
        for a_format in formats :
            if a_format['fields']['name'] not in core_format_names :
                a_format['pk'] = len(my_formats)+1
                my_formats.append(a_format)            
        output = open(formats_path,'w')     
        output.write(json.dumps(my_formats, indent=4))     
        output.close()  
        
        
        
        
help_str = """
python ckan_main.py scrape 'http://datahub.io/' options 
python ckan_main.py debug debug_items options

debug_items
    robots
    licenses
    package_list
    spam
    convert

options
    "{'site':'http://datahub.io/',
      'datasets':'../data/
      'licenses':'../data/
      'formats':'../data/
      'datacatalogs':'../data/
      'datarelations':'../data/
      'organizations':'../data/
      'scientists':'../data/
      
"""

if __name__ == "__main__":
    print("running as main")
    if len(sys.argv) <= 1 :
        print(help_str)
        sys.exit()
    if len(sys.argv) >= 3 :
        #read options here                             
        datasets_path = data_root + 'datasets.json'
        my_licenses_path = data_root + 'my_licenses.json'
        formats_path = data_root + 'formats.json'
        datacatalogs_path = data_root + 'datacatalogs.json'
        datarelations_path = data_root + 'datarelations.json'
        organizations_path = data_root + 'organizations.json'
        scientists_path = data_root + 'scientists.json'
        site_root = 'http://datahub.io/'
        options = {}
        try:
            if len(sys.argv) >= 4 :
                options = eval(sys.argv[3])                       
                if 'site' in options:
                    site_root = options['site']
                if 'datasets' in options:
                    datasets_path = options['datasets']
                if 'licenses' in options:
                    my_licenses_path = options['licenses']
                if 'formats' in options:
                    formats_path = options['formats']
                if 'datacatalogs' in options:
                    datacatalogs_path = options['datacatalogs']
                if 'datarelations' in options:
                    datarelations_path = options['datarelations']
                if 'organizations' in options:
                    organizations_path = options['organizations']              
                if 'scientists' in options:
                    scientists_path = options['scientists']         
        except SyntaxError as e :            
            print("main read options, reason: ", e.reason) 
            
        if sys.argv[1] == 'debug' :
            for debug_item in sys.argv[2].split(','):
                print(debug_item)
                if debug_item == 'robots' :
                    ckan_test_robots(site_root)     
                if debug_item == 'licenses' :
                    ckan_test_licenses(site_root, core_licenses_path, my_licenses_path)
                if debug_item == 'package_list' :
                    ckan_test_package_list(site_root, 10)
                if debug_item == 'package_read' :
                    ckan_test_package_read(site_root, 'ckan_package_list.json', 'ckan_datasets.json', 10)
                if debug_item == 'spam' :
                    ckan_test_spam_score('ckan_datasets.json', 'scored_datasets.json')          
                if debug_item == 'convert' :
                    #ckan_test_convert_package('ckan_datasets.json')  
                    ckan_test_convert_package('scored_datasets.json')
    
