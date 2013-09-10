#!/usr/bin/python

import re
import json

spam_def ={
              "len(title)==1" : 100,
              "len(notes)==0 or 1" : 100,
              "len(notes)>1000" : 100,
              "800<len(notes)<=1000" : 50,
              "url only notes" : 10,
              "each long word 25" : 10,
              "len(author)==0 or 1" : 5,
              "len(maintainer)==0 or 1" : 5,
              "len(description)>2000" : 10,
              "num resources==0" : 3000,
              
              "spam words" : {    "30" : "sale, buy, coupon, cheap",
                                  "15" : "terrific, great, genuinely, quite, pleasant, fortunately, tricks, tip, risk",
                                  "15" : "certainly",
                                  "8" : "!, ?",
                                  "6" : "your, my, they, them, their,",
                                  "10" : "advice, should, how to, shopping, how does, outlet, truly, fashion, Ins And Outs, reasons why, amazing, undoubtedly, fun, helpful, enhance, look of, easy, in order to, ever, again, excellent, even, discounts, pleased, become, industry professionals, are saying, possible, really, virtually, super, huge, favored, enhancement, risk-free,fancy, thrilling, recognizable, especially",
                                  "5" : "very, perhaps, ways to, first step, things, know, need, thought, truth, basic, understand, personal, many, suitable, as well as, actually, where, what, might, will, everything, often, a lot, assume, understood, misunderstood, misunderstand, In that case, possibility, expert, effortlessly, learn to, guide, even, without, do not, hestitant, can, enjoy, anything, ordered, simple"
                             }
                              
}



# take a ckan package and return spam score    
def add_spam_score(ckan_package) :
    print(ckan_package['title']) 
    spam_score = float(0) 
    if ckan_package['title'] == None or len(ckan_package['title'].split(' ')) <= 1 :
        spam_score = spam_score + spam_def["len(title)==1"] 
    if ckan_package['notes'] == None or len(ckan_package['notes'].split(' ')) <= 1 :  
        spam_score = spam_score + spam_def["len(notes)==0 or 1"] 
    if ckan_package['notes'] != None :
        if len(ckan_package['notes']) > 1000 :  
            spam_score = spam_score + float(len(ckan_package['notes']))/1000 * spam_def["len(notes)>1000"] 
        elif len(ckan_package['notes']) > 800 : 
            spam_score = spam_score + spam_def["800<len(notes)<=1000"] 
        word_score = 0
        for score in spam_def['spam words'] :
            for word in spam_def['spam words'][score].split(",") :
                word_score = word_score + len(re.findall(r'\s'+word+'[s]?\s',ckan_package['notes'],flags=re.I or re.S))*int(score)  
        spam_score = spam_score + (word_score / (float(len(ckan_package['notes'])+1)/100))   
    if ckan_package['num_resources'] == 0 :
        spam_score = spam_score + spam_def["num resources==0"] 
    for each_resource in ckan_package['resources'] :
        if len(each_resource['description']) > 2000 :
            spam_score = spam_score + spam_def["len(description)>2000"]  
    return spam_score      
        