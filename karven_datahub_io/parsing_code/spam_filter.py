#!/usr/bin/python

import re
import json
import math
from operator import itemgetter, attrgetter
from shared_functions import convert_json   
from shared_functions import append_file  

spam_def ={
              "len(title)==1" : 100,
              "len(notes)==0 or 1" : 100,
              "len(notes)>1000" : 100,
              "800<len(notes)<=1000" : 50,
              "url only notes" : 10,
              "each long word 25" : 10,
              "len(author)==0 or 1" : 500,
              "len(maintainer)==0 or 1" : 500,
              "len(description)>1000" : 100,
              "num resources==0" : 3000,
              "really long word" : 25,
              "strange license" : 500, 
              
              "spam words" : {    "100" : "sale, buy, coupon, discounts, shopping, outlet, risk-free, cheap",
                                  "30" : "certainly, wrong, easy, quick, simple, terrific, fancy, thrilling, amazing, great, genuinely, quite, pleasant, fortunately, tricks, tip, risk, pleasing, pleased, truly, fashion, famous, undoubtedly, fun, helpful, enhance, effortlessly, possible, really, virtually, super, huge, favored, enhancement, excellent",
                                  "80" : "\!, \?",
                                  "60" : "your, my, they, them, their, you are, you're",
                                  "15" : "should, might, will, may",
                                  "10" : "advice, how to, how does, Ins And Outs, reasons why, look of, in order to, ever, again, even, become, industry professionals, are saying, recognizable, especially",
                                  "5" : "very, perhaps, ways to, first step, things, know, need, thought, truth, basic, understand, personal, many, suitable, as well as, actually, where, what, everything, often, a lot, assume, understood, misunderstood, misunderstand, In that case, possibility, expert, learn to, guide, even, without, do not, hestitant, can, enjoy, anything, ordered"
                             }
                              
}

max_word_length = 30

# take a ckan package and return spam score    
# need to append spam_digest
def add_spam_score(ckan_package, spam_digest) :
    #print(ckan_package['name']) 
    digest = { 'datahub_name':ckan_package['name'] }
    spam_score = float(0) 
    if ckan_package['author'] == None or len(ckan_package['author'].split()) <= 1 :
        spam_score = spam_score + spam_def["len(author)==0 or 1"]
        digest["one word author"] = ckan_package['author']
        digest["author"] = spam_def["len(author)==0 or 1"] 
    if ckan_package['maintainer'] == None or len(ckan_package['maintainer'].split()) <= 1 :
        spam_score = spam_score + spam_def["len(maintainer)==0 or 1"]
        digest["one word maintainer"] = spam_def["len(maintainer)==0 or 1"] 
        digest["maintainer"] = ckan_package['maintainer']
    if ckan_package['title'] == None or len(ckan_package['title'].split()) <= 1 :
        spam_score = spam_score + spam_def["len(title)==1"]
        digest["one word title"] = spam_def["len(title)==1"] 
    if ckan_package['notes'] == None or len(ckan_package['notes'].split()) <= 1 :  
        spam_score = spam_score + spam_def["len(notes)==0 or 1"]        
        digest["one or zero word notes"] = spam_def["len(notes)==0 or 1"] 
             
    if ckan_package['notes'] != None :
        #find longest word in notes
        words_len = sorted([{'word':x, 'len':len(x)} for x in unicode(ckan_package['notes']).split()], key=itemgetter('len'), reverse=True) 
        word_score = 0
        longest_word = None
        for word_len_pair in words_len :
            if word_len_pair['len'] > max_word_length :
                # need to skip http, ftp, file b/c they are links
                if not re.search(r'(http|ftp|file)',word_len_pair['word']) :
                    word_score = word_score + math.pow(word_len_pair['len'] - max_word_length,2) * spam_def["really long word"]    
                    if not longest_word :
                        longest_word = word_len_pair
            else :
                digest["longest word in notes"] = longest_word #len(notes) may be zero 
                digest["long words in notes"] = word_score
                digest["len(notes)"] = len(ckan_package['notes'])
                break
        spam_score = spam_score + word_score
        #find spam words in notes
        if len(ckan_package['notes']) > 1000 :  
            temp_num = math.pow(float(len(ckan_package['notes']))/1000,2) * spam_def["len(notes)>1000"]
            spam_score = spam_score + temp_num 
            digest["len(notes) score"] = temp_num
        elif len(ckan_package['notes']) > 800 : 
            spam_score = spam_score + spam_def["800<len(notes)<=1000"] 
            digest["len(notes) score"] = spam_def["800<len(notes)<=1000"] 
        word_score = 0
        spam_words = ""
        for score in spam_def['spam words'] :
            for word in spam_def['spam words'][score].split(",") :
                temp_num = len(re.findall(r'\s'+word.strip()+'[s]?\s',ckan_package['notes'],flags=re.I or re.S))*int(score) 
                #re.I = Ignore case, re.S = . also matches newline
                word_score = word_score + temp_num    
                if temp_num > 0 :      
                    spam_words = spam_words + " , " + word + "-" + str(temp_num)
        digest["spam word scores"] = spam_words
        digest["spam words"] = word_score
        spam_score = spam_score + word_score #/ (float(len(ckan_package['notes'])+1)/100))   
    #resources      
    digest["num_resources"] = ckan_package['num_resources']        
    if ckan_package['num_resources'] == 0 :
        spam_score = spam_score + spam_def["num resources==0"]              
        digest["no resource"] = spam_def["num resources==0"]       
    digest["len(resources description) > 1000"] = 0
    for each_resource in ckan_package['resources'] :
        if len(each_resource['description']) > 1000 :
            temp_num = math.pow(float(len(each_resource['description']))/1000,2) * spam_def["len(description)>1000"]
            spam_score = spam_score + temp_num         
            digest["len(resources description) > 1000"] = digest["len(resources description) > 1000"] + temp_num
    digest['spam_score'] = spam_score
    
    append_file(spam_digest, convert_json(digest) + ",")
    print(ckan_package['name'] + " : " + str(spam_score)) 
    return spam_score      
        