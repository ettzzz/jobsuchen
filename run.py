#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 09:38:46 2019

@author: eriti
"""


import time
import random
from job_db import jobDB
from bot import tell_my_bot
from spider import jobSpider
from lokale.var import token, chat_id

def main():
    crawls_per_day = 3 # frequency of the crawling
    job_cfgs = {
        'python': {'stop':['弹性','大专' ], 'go':['应届','海外','硕士','quirement']},
        '智能交通': {'stop':['弹性','轨道','大专'], 'go':['应届','海外','硕士']},
        '交通工程': {'stop':['弹性','轨道','大专'], 'go':['应届','海外','硕士']},
        '智慧交通': {'stop':['弹性','轨道','大专'], 'go':['应届','海外','硕士']},
        }
    
    messager = tell_my_bot(token, chat_id)
    agent = jobSpider(job_cfgs)
    db = jobDB()
    
    while True:
        counter = 0
        while counter < crawls_per_day: 
            t_start = time.time()
            for each_keyword in list(job_cfgs.keys()):
                each_job_list = agent.scheduler(each_keyword)
                db.insert(each_job_list)
            t_crawl = int(time.time() - t_start())
            counter += 1
            t_sleep = 86400/crawls_per_day - t_crawl + random.randint(-600, 600)
            t_sleep = t_sleep if t_sleep > 0 else 0
            time.sleep(t_sleep)
#            time.sleep(3)
        messager.send_to_me(db.fetch())
        db.clean()
        if db.pool_check():
            messager.pool_reminder(db.pool_level())

            
if __name__ == '__main__':
    main()

