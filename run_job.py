#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 09:38:46 2019

@author: eriti
"""


import time
import random
import re
from job_db import jobDataBase
from bot import tellMyBot
from spider import jobSpider
from local_var import token, chat_id

job_cfgs = {
            'global':{
                    'crawls_per_day':3,
                    'crawl_size':90,
                    'db_name': 'jobs.db',
                    'ptable_name':'pool',
                    'njtable_name':'',
                    'ctable_name':'citysets',
                    'cities':['beijing','shanghai','shenzhen'],
                    },
            'jobs':{
                'python后端': {'stop':['++','adoop','精通'], 'go':['应届','raduate']},
                'python': {'stop':[ '++','crapy','ava','计算机'], 'go':['应届','raduate']},
                '智能交通': {'stop':['轨','CAD','Auto'], 'go':['应届','研究','硕士']},
                '交通工程': {'stop':['抗压','轨','CAD','Auto'], 'go':['应届','研究', '硕士']},
                },
           'filters':{
                'company_stops':['轨','百度','aidu'],
                'position_stops':['轨','汽','实习','Intern','售','经理','高级','资深','总监','ava','++',],
                },
             'cities':{
                'shanghai':{
                            'linkedin':{'location':'shanghai', 'locationId':'STATES.cn.sh'},
                            'indeed':'上海市',
                            'liepin':'020',
                            'zhilian':'538',
                            'lagou':'上海',
                            'bosszhipin':'101020100'
                            },
                'beijing':{
                            'linkedin':{'location':'beijing', 'locationId':'STATES.cn.bj'},
                            'indeed':'北京',
                            'liepin':'010',
                            'zhilian':'530',
                            'lagou':'北京',
                            'bosszhipin':'101010100'
                            },
                'shenzhen':{
                            'linkedin':{'location':'shenzhen', 'locationId':'PLACES.cn.18-9'},
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
            table_name = 'table' + time.strftime('%m%d%H%M',time.localtime(time.time()))
            db.addTable(table_name)
            for each_keyword in list(cfgs['jobs'].keys()):
                each_job_list = agent.scheduler(each_keyword)
                db.insert(table_name, each_job_list)
            
            print('main: Sending messages to bot...')
            messager.send2me(db.fetch(table_name))
            
            t_crawl = int(time.time() - t_start)
            t_sleep = 86400/crawls_per_day - t_crawl + random.randint(-600, 600)
            t_sleep = t_sleep if t_sleep > 0 else 0
#            time.sleep(t_sleep)
            time.sleep(3) # for test purpose
            counter += 1
            
        if db.pool_check():
            messager.poolAlert(db.pool_level())
            
if __name__ == '__main__':
    main(job_cfgs)

