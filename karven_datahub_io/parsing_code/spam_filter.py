#!/usr/bin/python

import re
import json
import math
from operator import itemgetter, attrgetter
from shared_functions import convert_json   
from shared_functions import append_file  

spam_def ={
              "len(title)==1" : 100,
              "len(notes)==0 or 1" : 500,
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
              
              "spam words" : {    "1000" : "buy, cheap, coupon, credit card, discounts, outlet, paypal, risk-free, sale, shopping, sold, style",
                                  "100" : "accessories, beauty, bra, clothing, computer, cosmetics, fashion, gucci, hangbag, nike, styling",
                                  "100" :"certainly, excellent, great, helpful, possible, quite, really, truly, undoubtedly, unquestionably, virtually, wrong",
                                  "100" : "amazing, attractive, best, brilliant, chic, easy, effortless, effortlessly, elegance, enhance, enhancement, enormous, exclusive, fabulous, famous, fancy, favored, fortunately, fun, generously, genuinely, huge, iconic, immaculate, newest, pleasant, pleased, pleasing, popular, quick, risk, sadly, shiny, simple, stylish, super, terrific, thrilling, tip, tricks, unfortunately",
                                  "80" : "\!, \?",
                                  "60" : "i'm, my, they, them, their, your, you are, you're",
                                  "15" : "should, might, will, may, can",
                                  "40" : "Ins And Outs, absolutely, advice, again, always, are saying, become, especially, essential, even, ever, extremely, how does, how to, in order to, industry professionals, look of, love, perhaps, reasons why, recognizable, slightly, usual, usually, ways to",
                                  "5" : "In that case, a lot, actually, anything, as well as, assume, basic, do not, enjoy, even, everything, expert, first step, guide, hestitant, know, learn to, many, misunderstand, misunderstood, need, often, ordered, personal, possibility, suitable, things, thought, truth, understand, understood, very, without"
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
    
    all_the_text = "" #all the text        
    if ckan_package['notes'] != None :
        all_the_text = all_the_text + " " + ckan_package['notes']     
        digest["len(notes)"] = len(ckan_package['notes'])
        if len(ckan_package['notes']) > 1000 :  
            temp_num = math.pow(float(len(ckan_package['notes']))/1000,2) * spam_def["len(notes)>1000"]
            spam_score = spam_score + temp_num 
            digest["len(notes) score"] = temp_num
        elif len(ckan_package['notes']) > 800 : 
            spam_score = spam_score + spam_def["800<len(notes)<=1000"] 
            digest["len(notes) score"] = spam_def["800<len(notes)<=1000"] 
            
    #resources      
    digest["num_resources"] = ckan_package['num_resources']        
    if ckan_package['num_resources'] == 0 :
        spam_score = spam_score + spam_def["num resources==0"]              
        digest["no resource"] = spam_def["num resources==0"]       
    digest["len(resources description) > 1000"] = 0
    for each_resource in ckan_package['resources'] :             
        if 'description' in each_resource and each_resource['description'] != None :
            all_the_text = all_the_text + " " + each_resource['description']        
        if len(each_resource['description']) > 1000 :
            temp_num = math.pow(float(len(each_resource['description']))/1000,2) * spam_def["len(description)>1000"]
            spam_score = spam_score + temp_num         
            digest["len(resources description) > 1000"] = digest["len(resources description) > 1000"] + temp_num
    #find longest word in notes
    #words_len = sorted([{'word':x, 'len':len(x)} for x in unicode(all_the_text).split()], key=itemgetter('len'), reverse=True)  
    words_len = sorted([{'word':x.strip(), 'len':len(x.strip())} for x in re.findall(r'\W\w.*?\W',all_the_text,flags=re.I or re.S)], key=itemgetter('len'), reverse=True) 
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
            if not longest_word :
                longest_word = words_len[0]
            digest["longest word in notes + descriptions"] = longest_word #len(notes) may be zero 
            digest["long words in notes + descriptions score"] = word_score
            break
    spam_score = spam_score + word_score
    #find spam words in notes
    word_score = 0
    spam_words = ""
    for score in spam_def['spam words'] :
        for word in spam_def['spam words'][score].split(",") :
            temp_num = len(re.findall(r'\W'+word.strip()+'[s]?\W',all_the_text,flags=re.I or re.S))*int(score) 
            #re.I = Ignore case, re.S = . also matches newline
            #\W When the LOCALE and UNICODE flags are not specified [a-zA-Z0-9_]
            word_score = word_score + temp_num    
            if temp_num > 0 :      
                spam_words = spam_words + " , " + word + "-" + str(temp_num)
    digest["spam word scores"] = spam_words
    digest["spam words"] = word_score
    spam_score = spam_score + word_score #/ (float(len(ckan_package['notes'])+1)/100))   
    
    digest['spam_score'] = spam_score
    if spam_digest :
        append_file(spam_digest, convert_json(digest) + ",")
    print(ckan_package['name'] + " : " + str(spam_score)) 
    return spam_score      
        