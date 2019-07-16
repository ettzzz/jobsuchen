#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 09:38:46 2019

@author: eriti
"""
'''
1. title filter comes back
2. add db tables when each crawl
3. new stop words for censor Auto CAD ++ 年以上
4. new stop words for filtering: 轨道 in company
5. check crawl results
6. zhilian is 25 zai or not

'''

import time
import random
import re
from job_db import jobDataBase
from bot import tellMyBot
from spider import jobSpider
from lokale.var import token, chat_id

job_cfgs = {
            'global':{
                    'crawls_per_day':3,
                    'crawl_size':100,
                    'db_name': 'Arbeitsuchen.db',
                    'jtable_name':'Arbeiten',
                    'ptable_name':'Bad',
                    'ctable_name':'Staedte',
                    'cities':['beijing','shanghai','shenzhen'],
                    },
            'jobs':{
                'python后端': {'stop':['++','adoop','3年以上'], 'go':['应届','quirement','raduate']},
                'python': {'stop':[ '++','crapy','ava','3年以上'], 'go':['应届','quirement','raduate']},
                '智能交通': {'stop':['轨道','CAD','Auto'], 'go':['应届','海外',]},
                '交通工程': {'stop':['抗压','轨道','CAD','Auto'], 'go':['应届','海外',]},
                '智慧交通': {'stop':['轨道','CAD','Auto'], 'go':['应届','海外',]},
                },
            'filters':{
                'company_stops':['轨道','百度','aidu'],
                'position_stops':['轨道','汽车','实习','售','经理','高级','资深','总监','ava','++',],
                },
            'cities':{
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
                        },
                },
            }


def main(cfgs):
    crawls_per_day = cfgs['global']['crawls_per_day']
    messager = tellMyBot(token, chat_id)
    agent = jobSpider(cfgs)
    db = jobDataBase()
    # future todos: change the structure of cfgs, categories: global, bot, db, spider,
    
    while True:
        counter = 0
        while counter < crawls_per_day: 
            t_start = time.time()
            table_name = time.strftime('%m%d%H%M',time.localtime(time.time()))
            for each_keyword in list(cfgs['jobs'].keys()):
                each_job_list = agent.scheduler(each_keyword)
                db.insert(table_name, each_job_list)
            
            messager.send2me(db.fetch(table_name))
            
            t_crawl = int(time.time() - t_start)
            t_sleep = 86400/crawls_per_day - t_crawl + random.randint(-600, 600)
            t_sleep = t_sleep if t_sleep > 0 else 0
            time.sleep(t_sleep)
            time.sleep(3) # for test purpose
            counter += 1
            
        if db.pool_check():
            messager.poolAlert(db.pool_level())
            
if __name__ == '__main__':
    main(job_cfgs)

