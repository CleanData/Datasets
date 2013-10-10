                            
import datetime
import re          
from time import sleep      
import sys
import json            
import urllib
import urllib2                                                     

  


CrawlDelay = 2
spider_name = "Python-urllib/2.7 CleanData_OpenDataResearch"
headers = { 'User-Agent' : spider_name }

data_root = ''
datasets_path = data_root + 'datasets.json'
my_licenses_path = data_root + 'my_licenses.json'
formats_path = data_root + 'my_formats.json'
datacatalogs_path = data_root + 'datacatalogs.json'
datarelations_path = data_root + 'datarelations.json'
organizations_path = data_root + 'organizations.json'
scientists_path = data_root + 'scientists.json'
saved_state = 'saved_state.json'
                                        
core_licenses_path = 'licenses.json'
core_formats_path = 'formats.json'

#existing_licenses=["Public Domain Dedication and License (PDDL)","Open Data Commons Attribution License (ODC-By)","Open Data Commons Open Database License (ODC-ODbL)","CC0","public domain","GNU General Public License (GPL)","MIT","Apache 2.0","BSD 3-Clause License","BSD 2-Clause License","GNU Lesser Public License v3.0","Mozilla Public License v2.0","Common Development and Distribution License 1.0","Eclipse Public License","Unknown","Copyright"]

#existing_formats=["JSON","GeoJSON","TopoJSON","XML","xls","xlsx","CSV","TSV","PDF","Shapefile","Geodatabase","mongoDB","SQLite","mySQL","PostgreSQL","ROOT","Fits","Mapbox Map"]

def read_url(url, delay=3, values={}): #read url and return the content
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

# read file to json
def read_json(file_path) :          
    f = open(file_path)     
    if f :
        json_object = json.loads(f.read())     
        f.close()
        return json_object
    return [] 
    
def write_json(file_path, json_object) :          
    output = open(file_path,'w')     
    output.write(json.dumps(json_object, indent=4))     
    output.close() 

#################################################################################################       
  
#https://data.cityofnewyork.us/api/views.json?limit=200&page=2
page_count = 1
metadata_url_base = "https://data.cityofnewyork.us/api/views.json?limit=200&page=" 
#metadata_url_base = "https://data.cityofnewyork.us/api/views.json?limit=5&page="
dataset_url_base = "https://nycopendata.socrata.com/resource/"
dataset_url_base2 = "https://data.cityofnewyork.us/api/views/"
domain_url = "https://data.cityofnewyork.us/"
user_url_base = "https://data.cityofnewyork.us/profile/"

datasets = []
formats = []
organizations = []
scientists = []

if __name__ == "__main__":
    print("running as main")
    if len(sys.argv) > 1 and sys.argv[1] == "continue":
        datasets = read_json(datasets_path)
        organizations = read_json(organizations_path)
        scientists = read_json(scientists_path)
        page_count = int(read_json(saved_state)) + 1
        print(read_json(saved_state))
                                                              
page_json = json.loads(read_url(metadata_url_base + str(page_count)))

while page_json :
    for d in page_json :
        #
        a_dataset={"model":"data_connections.Dataset","pk":None,"fields":{
          	"url": "",             
          	"name": "",                                   
          	"description": "",
          	"data_format": [],           
          	"date_last_edited": "",
          	"date_published": "",
          	"manager": None,
          	"managing_organization": None,                   
          	"license": [],
          	"data_catalog": None
        }}
        print(d['id'] + " : " + d["name"])
        a_dataset["fields"]["socrata_id"] = d["id"]
        a_dataset["fields"]["url"] = dataset_url_base +d["id"]
        #a_dataset["fields"]["url"] = domain_url + +d["category"] + "/" + d["name"] + "/" + d["id"
        a_dataset["fields"]["name"] = d["name"]
        if "description" in d :
            a_dataset["fields"]["description"] = d["description"] 
        
        if "displayType" in d :
            a_dataset["fields"]["data_format"] = d["displayType"]
            if d["displayType"] and d["displayType"] not in [ f['fields']['name'] for f in formats ] : 
                a_format = { "model":"data_connections.Format", "pk":None, 'fields':{} }
                a_format['fields']['name'] = d["displayType"]              
                a_format['fields']['url'] = ''
                formats.append(a_format)
        
        
        scientist_name = d["owner"]["displayName"].rsplit(None,1)
        if len(scientist_name) == 1 :
            scientist_name.append("")            
        scientist_url = user_url_base + d["owner"]["id"]       
        a_dataset["fields"]["manager"] = [scientist_name[0], scientist_name[1], scientist_url]           
        if scientist_url not in [ s['fields']['profile_url'] for s in scientists ] :    
            a_scientist = { "model":"data_connections.Scientist", "pk":None, 'fields':{
                "firstname" : scientist_name[0],       
                "lastname" : scientist_name[1],       
                "profile_url" : scientist_url
            } }                     
            scientists.append(a_scientist)        
        
        #a_dataset["fields"]["managing_organization"] = [ d["attribution"] ]    
        x = json.loads(read_url(dataset_url_base2 + d["id"]))         
        if "attribution" in x:      
            a_dataset["fields"]["managing_organization"] = [ x["attribution"] ]    
            if x["attribution"] > 0 and x["attribution"] not in [ o["fields"]["name"] for o in organizations ] : 
                a_organization = { "model":"data_connections.Organization", "pk":None, 'fields':{} }
                a_organization['fields']['name'] = x["attribution"]           
                a_organization['fields']['url'] = '' 
                organizations.append(a_organization)                                    
        
        a_dataset["fields"]["date_last_edited"] = datetime.datetime.fromtimestamp(d["viewLastModified"]).strftime('%Y-%m-%dT%H:%M:%SZ')
        a_dataset["fields"]["date_published"]=datetime.datetime.fromtimestamp(d["publicationDate"]).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        socrata_license =  { lic.lower() for flags in [ g["flags"] for g in d["grants"] if "flags" in g ] for lic in flags }
        if "public" in socrata_license :
            a_dataset["fields"]["license"]=["public"]
        else :
            a_dataset["fields"]["license"]=["Unknown"]
        datasets.append(a_dataset)
    #end of current page
    
    write_json(datasets_path, datasets)                  
    write_json(organizations_path, organizations)
    write_json(scientists_path, scientists)  
    f = open(core_formats_path)
    core_formats = json.loads(f.read())
    core_format_names = [ item['fields']['name'].lower() for item in core_formats ]
    f.close()
    my_formats = []
    for a_format in formats :
        if a_format['fields']['name'].lower() not in core_format_names :
            a_format['pk'] = len(my_formats)+1
            my_formats.append(a_format)          
    write_json(formats_path, my_formats)   
    write_json(saved_state, str(page_count))  
    #page(page_count) completed, if not written, that means this page is not done  
    #output = open(saved_state,'w')     
    #output.write(page_count)     
    #output.close()
    
    page_count = page_count + 1
    page_json = json.loads(read_url(metadata_url_base + str(page_count)))
    
    
licenses = [{ 'fields':{ "name":"public", "url":"" } }]  

 
write_json(datasets_path, datasets)                  
write_json(organizations_path, organizations)
write_json(scientists_path, scientists)        
write_json(saved_state, str(page_count))
                  
f = open(core_formats_path)
core_formats = json.loads(f.read())
core_format_names = [ item['fields']['name'].lower() for item in core_formats ]
f.close()
my_formats = []
for a_format in formats :
    if a_format['fields']['name'].lower() not in core_format_names :
        a_format['pk'] = len(my_formats)+1
        my_formats.append(a_format)          
write_json(formats_path, my_formats)  
write_json(my_licenses_path, licenses) 
 