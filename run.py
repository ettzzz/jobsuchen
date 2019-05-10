#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 09:38:46 2019

@author: eriti
"""


'''
job suchen run.py
Struktur:
    DataBase
    Notifikation über den Bot
    Spider über den Websites
    Filtrieren
    
(UID,Source:Position,Release,Company,Location,Payment,URL,Keyword)
'''

import time
import random
from job_db import jobDB
from bot import tell_my_bot
from spider import jobSpider


def main():
    crawls_per_day = 3
    job_cfgs = {
        'python': {'stop':['弹性','大专' ], 'go':['应届','海外','硕士','quirement']},
        '智能交通': {'stop':['弹性'], 'go':['应届','海外','硕士']},
        '数据分析': {'stop':['弹性','大专'], 'go':['应届','海外','硕士']},
        }
    
    messager = tell_my_bot()
    agent = jobSpider(job_cfgs)
    db = jobDB()
    
    while True:
        counter = 0
        while counter < crawls_per_day: # frequency of the crawling
            for each_keyword in list(job_cfgs.keys()):
                each_job_list = agent.scheduler(each_keyword, fast=True)
                db.insert(each_job_list)
        
            counter += 1
            time.sleep(3600*24/crawls_per_day + random.randint(-5000, 5000))
        
        messager.send_to_me(db.fetch())
        if db.pool_check():
            messager.pool_reminder(db.pool_level())

            
if __name__ == '__main__':
    main()
