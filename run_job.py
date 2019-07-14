#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 09:38:46 2019

@author: eriti
"""


import time
import random
from job_db import jobDataBase
from bot import tellMyBot
from spider import jobSpider
from lokale.var import token, chat_id

job_cfgs = {
            'jobs':
                {
                'python后端': {'stop':['大专', '专科', '抗压','adoop',], 'go':['应届','海外','硕士','研究生','quirement','raduate','JavaScript']},
                'python爬虫': {'stop':['大专', '专科', '抗压','crapy','ava'], 'go':['应届','海外','硕士','研究生','quirement','raduate']},
                'python数据分析': {'stop':['大专','adoop','抗压','数学'], 'go':['应届','海外','硕士','quirement','raduate']},
                '智能交通': {'stop':['轨道','大专', '专科',], 'go':['应届','海外','硕士','研究生',]},
                '交通工程': {'stop':['轨道','大专', '专科',], 'go':['应届','海外','硕士','研究生',]},
                '智慧交通': {'stop':['轨道','大专', '专科',], 'go':['应届','海外','硕士','研究生',]},
                },
            'filters':
                {
                'company_stops':['某','一线','知名','百度','aidu'],
                'position_stops':['实习','销售','经理','高级','资深','文案','ava','++',],
                },
            'cities':
                {
                'shanghai':{
                            'linkedin':'cnERSATZ3A8909',
                            'indeed':'上海',
                            'liepin':'020',
                            'zhilian':'538',
                            'lagou':'上海',
                            'bosszhipin':'101020100'
                            },
                'beijing':{
                            'linkedin':'cnERSATZ3A8911',
                            'indeed':'北京',
                            'liepin':'010',
                            'zhilian':'530',
                            'lagou':'北京',
                            'bosszhipin':'101010100'
                            },
                'shenzhen':{
                            'linkedin':'cnERSATZ3A8910',
                            'indeed':'深圳',
                            'liepin':'050090',
                            'zhilian':'765',
                            'lagou':'深圳',
                            'bosszhipin':'101280600'
                        }
                },

            }


def main(configurations):
    crawls_per_day = 3 # frequency of the crawling
    messager = tellMyBot(token, chat_id)
    agent = jobSpider(configurations)
    db = jobDataBase()
    
    while True:
        counter = 0
        while counter < crawls_per_day: 
            t_start = time.time()
            for each_keyword in list(configurations['jobs'].keys()):
                each_job_list = agent.scheduler(each_keyword)
                db.insert(each_job_list)
            t_crawl = int(time.time() - t_start)
            counter += 1
            t_sleep = 86400/crawls_per_day - t_crawl + random.randint(-600, 600)
            t_sleep = t_sleep if t_sleep > 0 else 0
            time.sleep(t_sleep)
            time.sleep(3)
        messager.send2me(db.fetch())
        db.clean()
        if db.pool_check():
            messager.poolAlert(db.pool_level())
            
if __name__ == '__main__':
    main(job_cfgs)

