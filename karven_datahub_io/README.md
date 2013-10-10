Issues 
======

###  Datahub
When datahub returns internal server error, the script sleeps for 50 seconds and retry.
 
And there are a lot of spam. May need to filter again.      

Crawl-Delay : 10 seconds. 
Needs one request to pull package, and one more for non-spam to get relations

###  Code
The current code should work for all ckan implementing sites.
Codes in testing stages should run only from files to minimize datahub accesses.

copied exameple datasets.json and formats.json to parsing_code directory b/c comments on first line cannot be parsed

Natural Language Processing doesn't work for spam filtering b/c of good adjectives like collaborative, statistical. 
Datasets with zero resources are dropped from data/datasets.json automatically.


*****

Running the scripts
===================
### To run through the entire site 
##### python ckan_main.py scrape "{options}"
This process can be interrupted by user. The script will save state after interrupt.   
   
### To continue from a previous run   
##### python ckan_main.py continue "{options}"

    python ckan_main.py continue
   
Continue running from last session with default options.

### For debugging
##### python ckan_main.py debug debug_items "{options}"

    python ckan_main.py debug relations
   
This command retrieves data relations for datasets in `data/datasets.json`

### debug_items
#### robots
read the robots.txt and print the crawl-delay for the website    
#### licenses
Read the licenses used by the ckan site and output to `my_licenses.json`. 
There may be other licenses used by the datasets though.
#### package_list
Read the list of packages available on the site and write to `ckan_package_list.json`
#### package_read
Read the ckan packages and save it unchanged to `ckan_datasets.json`
#### spam
add a spam score to the datasets in `ckan_datasets.json` and saved the data to `scored_datasets.json`
#### convert
convert `scored_datasets.json` to proper Datasets formats.
#### relations
just retrieve data relations for alread read datasets
#### relations_continue
continue retrieving from previously unfinished data relations

### "{options}"
Default options

    options = "{'site':'http://datahub.io/',
          'datasets':'../data/datasets.json'
          'licenses':'../data/my_licenses.json'
          'formats':'../data/formats.json'
          'datacatalogs':'../data/datacatalogs.json'
          'datarelations':'../data/datarelations.json'
          'organizations':'../data/organizations.json'
          'scientists':'../data/scientists.json'}"
      
      
*****

Extra files
===========

####parsing_code/saved_state.json
saves the `ckan_object["name"]` and the last modified time of the already processed datasets        

####parsing_code/processed_relations.json
saves the `ckan_object["name"]` of the datasets after processing the data relation  

####parsing_code/spam_digest.json
Generate by `spam_filter.py`. Information about dataset spam score. It is written as each dataset is passed through the spam filter.

The scores are pretty arbitrary, but sort of works. A better way is to create an initial spam words list. Then recursively add words and weights from spam datasets to that list and sutract words from legitimate datasets from the list.

`spam_filter.py` was modified a few times during the current run. The earlier spam digest may have less information.

 - `datahub_name` is the `ckan_object["names"]`
 - `spam_score` is the total spam score
 - `len(notes)`, `len(notes) score` stores the number of characters in `ckan_object["notes"]` and the spam score assigned according to the length
 - `one word author`, `author` stores the author and the spam score if the author has zero or one word. (mistakenly reversed the printout, already fixed in code) 
 - `one word maitainer`, `maintainer` stores the maintainer and the spam score if the maintainer has only zero or one word.
 - `num_resources`, `no resource` stores the number of resources in the dataset and if there is no resource, add *no resource* score to the `spam_score`
 - `longest words in notes + descriptions` stores the longest word in `ckan_object["notes"]` and `ckan_object["resource"]["description"]`, not necessarily spam 
 - `longest words in notes + descriptions score`, for words longer than `max_word_length` which is *30* and not part of an url, add spam scores according to the length
 - `spam words` is the total score from spam words
 - `spam word score` stores the spam word and (the score for the word multiplied by the number of occurrence in `ckan_object["notes"]` and `ckan_object["resource"]["description"]`)  

For information about `ckan_object` see `dataset mapping` below. 


*****

References
==========

## ckan library reference
http://docs.ckan.org/en/ckan-2.0.2/api.html
sample dataset ny-zipcodes-and-electricity-use

    ckan_action_get = '/api/3/action/'
    package_list_path = ckan_action_get + 'package_list'
    package_show_path = ckan_action_get + 'package_show?id='
    license_list_path = ckan_action_get + 'licence_list'
    tag_list_path = ckan_action_get + 'tag_list'
    related_list_path = ckan_action_get + 'related_list?id='

Retrieve the identifiers for all the datasets
    
    http://datahub.io/api/3/action/package_list

Retrieve all the licenses                     
    
    http://datahub.io/api/3/action/licence_list

Retrieve a list of all the tags               
    
    http://datahub.io/api/3/action/tag_list
    
Example url for retrieving dataset

    http://datahub.io/api/3/action/package_show?id=ny-zipcodes-and-electricity-use

Example url for getting datarelation                   
            
    http://datahub.io/api/3/action/related_list?id=ny-zipcodes-and-electricity-use


## related list mapping to datarelations
http://datahub.io/api/3/action/related_list?id=ny-zipcodes-and-electricity-use

    {
        help: "Return a dataset's related items. Either the ``id`` or the ``dataset`` parameter must be given. :param id: id or name of the dataset (optional) :type id: string :param dataset: dataset dictionary of the dataset (optional) :type dataset: dictionary :param type_filter: the type of related item to show (optional, default: None, show all items) :type type_filter: string :param sort: the order to sort the related items in, possible values are 'view_count_asc', 'view_count_desc', 'created_asc' or 'created_desc' (optional) :type sort: string :param featured: whether or not to restrict the results to only featured related items (optional, default: False) :type featured: bool :rtype: list of dictionaries ",
        success: true,
        result: [
            {   #"how_data_was_processed" : ""
                #"source" : [this.url, this.title]
                #"derivative" : [dataset.url, dataset.name]
                #"datahub_name" : dataset.datahub_name
                view_count: 0,
                description: "A tool for visualizing NYC electricity use",
                title: "Energy Zip",
                url: "http://energyzip.org/",
                created: "2013-08-30T15:22:44.450720",
                featured: 0,
                image_url: "",
                type: "visualization",
                id: "9cfb97bc-e320-4b2d-acd7-b69899f7473c",
                owner_id: "69ef6802-09f1-48a0-8d0e-d8d931747900"
            },
            {
                view_count: 0,
                description: "2010 electricity consumption in kWh and GJ, by ZIP code, building type, and utility company.",
                title: "Electric Consumption By Zipcode",
                url: "https://data.cityofnewyork.us/Environment/Electric-Consumption-by-ZIP-Code-2010/74cu-ncm4?",
                created: "2013-08-30T15:22:06.426260",
                featured: 0,
                image_url: "",
                type: "api",
                id: "d847c7fd-469f-411f-9471-84d8205391a6",
                owner_id: "69ef6802-09f1-48a0-8d0e-d8d931747900"
            }
        ]
    }

## dataset mapping
```python
    {                                                      
        "id": "9da16c4f-32a1-43ac-ae6b-c3378c6e7e9f",                
        "type": "dataset",              
        "private": false, 
        "revision_timestamp": "2013-07-10T13:21:08.290922", 
        "metadata_created": "2011-03-25T20:54:45.839757",  # Dataset.data_created
        "metadata_modified": "2013-07-10T13:21:08.290922", # Dataset.date_last_edited  
        "state": "active", 
        "version": "",                                            
        "relationships_as_object": [],  
        "relationships_as_subject": [],    
        "revision_id": "24e1e151-9719-42cd-ae3c-f1837baf61b5"        
        
        "name": "enipedia", #                    
        "title": "Enipedia - Energy Industry Data", # Dataset.name; if num_resources > 1: DataCatalog.name 
        "isopen": true, 
        "url": "http://enipedia.tudelft.nl", # 
        "notes": "Enipedia is an active exploration into the applications of wikis and the semantic web for energy and industry issues. Through this we seek to create a collaborative environment for discussion, while also providing the tools that allow for data from different sources to be connected, queried, and visualized from different perspectives. \t", #             
        
        "organization": null,   
        "owner_org": null, 
        
        "author": "Enipedia Team @ Energy and Industry Section, TBM, Delft University of Technology", # Dataset.managing_organization, [name] put issue in issues on github , name url
        "author_email": "c.b.davis@tudelft.nl", 
        "maintainer": "Chris Davis and Alfredas Chmieliauskas", # Dataset.manager [first,last,url] Scientists                  
        "maintainer_email": "c.b.davis@tudelft.nl, a.chmieliauskas@tudelft.nl",  
        
        "license_id": "odc-pddl",                
        "license_title": "Open Data Commons Public Domain Dedication and Licence (PDDL)", # License.name, Datasets.[license] 
        "license_url": "http://www.opendefinition.org/licenses/odc-pddl", # License.url 
              
        "num_resources": 4, # if num_resources > 1 : this is a Data_Catalog 
        "resources": [
            {                                                 
                "id": "f4e0f840-4655-4564-b2d9-2b4f7996cfcb", 
                "name": "", # catalog.title + name + format                       
                "description": "Sparql endpoint", # (add catalog notes)  Dataset.description
                "mimetype": "text/html",        
                "mimetype_inner": "",       
                "resource_type": "file",                        
                "format": "api/sparql", # Dataset.[data_format] if this is empty or null, use mimetype
                "url": "http://enipedia.tudelft.nl/sparql", # Dataset.url
                "revision_timestamp": "2012-11-22T10:04:54.941937", 
                "last_modified": "2012-11-22T04:04:54.754872", # Dataset.date_last_modified date_published
                
                "cache_url": null, 
                "state": "active", 
                "webstore_url": null,                 
                "webstore_last_updated": null,            
                "cache_last_updated": null,       
                "hash": "", 
                "tracking_summary": {
                    "total": 0, 
                    "recent": 0
                }, 
                "position": 0, 
                "resource_group_id": "d2e47b75-d386-4adb-8026-4ab2db77231c", 
                "revision_id": "4af49ed1-8cc2-4384-8d26-7888639ce911", 
                "size": "20"
            }
        ], 
                
        "num_tags": 9, 
        "tags": [   #Dataset.tags[]
            {                                           
                "id": "833848ee-ef06-4283-bb26-164f6c3474b4"     
                "name": "crossdomain",                
                "display_name": "crossdomain",                        
                "revision_timestamp": "2011-08-14T20:49:47.638947", 
                
                "vocabulary_id": null, 
                "state": "active", 
            },
        ], 
        "tracking_summary": {
            "total": 649, 
            "recent": 17
        }, 
        "groups": [
            {
                "id": "74881ac4-abf2-4f8a-ba5a-1c92860c30de",    
                "name": "energy-data", 
                "title": "Energy Data"
                "description": "A collection of data about country level energy demand and energy generation technologies to the meet the demand with details of:\r\n\r\n- land area required for different energy generation sources\r\n- monetary cost of energy source to develop, implement, maintain and decommission, either by government or industry\r\n- location or suitable location\r\n- energy cost to make and maintain and decommission\r\n- time to develop\r\n- efficiency in cost/unit of energy \r\n- how efficiency is predicted to change over time\r\n\r\n\r\n ", 
            }
        ], 
        "extras": [
            {
                "key": "links:dbpedia", 
                "value": "1365", 
                "__extras": {
                    "package_id": "9da16c4f-32a1-43ac-ae6b-c3378c6e7e9f", 
                    "revision_id": "2bf90c67-c183-44aa-8c01-d90e0bcbe504"
                }
            }, 
            {
                "key": "links:open-energy-info-wiki", 
                "value": "189", 
                "__extras": {
                    "revision_id": "ccd4dd6c-cc99-4cab-91e7-64d471ca2824", 
                    "package_id": "9da16c4f-32a1-43ac-ae6b-c3378c6e7e9f"
                }
            }, 
            {
                "key": "links:world-factbook-fu-berlin", 
                "value": "204", 
                "__extras": {
                    "revision_id": "35d66d70-7bc5-4e41-b213-b30e0f2ce81d", 
                    "package_id": "9da16c4f-32a1-43ac-ae6b-c3378c6e7e9f"
                }
            }, 
            {
                "key": "namespace", 
                "value": "http://enipedia.tudelft.nl/wiki/", 
                "__extras": {
                    "revision_id": "14c2e6f9-b2b8-4d57-9dad-5145e7f77cc1", 
                    "package_id": "9da16c4f-32a1-43ac-ae6b-c3378c6e7e9f"
                }
            }, 
            {
                "key": "triples", 
                "value": "4180734", 
                "__extras": {
                    "package_id": "9da16c4f-32a1-43ac-ae6b-c3378c6e7e9f", 
                    "revision_id": "a803bb3e-2b6c-4509-9fed-3a25f78eb2e1"
                }
            }
        ], 
    }
```