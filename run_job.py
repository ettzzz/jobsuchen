#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 09:38:46 2019

@author: eriti
"""
'''
1. 一个输入文件
1.1 表名 每个用户一个呗
1.2 pool 每个用户也得一个了
2. citysets 什么时候能有 感觉快了
3. filter的整个逻辑需要再改善一下




'''



import time
import random
import gc
from job_db import jobDataBase
from bot import tellMyBot
from spider import jobSpider
from local_var import token, chat_id, browser_path

job_cfgs = {
            'global':{
#                    'crawls_per_day':6,
                    'crawls_per_day':1,
                    'crawl_size':25,
                    'db_name': 'jobs.db',
                    'ptable_name':'pool',
                    'ctable_name':'citysets',
                    'browser_path':browser_path,
                    },
            'filters':{
#                'company_stops':['百度','aidu','腾讯','银行'],
#                'position_stops':['实习','售','经理','高级','资深','总监','主管','专员','银行',],
                'company_stops':[],
                'position_stops':['总监','专员'],
                },
            'jobs':{
#                'python': {
#                        'cities':['shanghai', 'beijing'],
#                        'webs':['lagou','bosszhipin','indeed','liepin'],
#                        'title_red':['日语', 'php', 'ava', 'C', '自动','前端','课','讲'],
#                        'title_green':['ython','工程'],
#                        'description_red':['++','adoop','ocker','Vue','大专','专科'], 
#                        'description_green':['应届','raduate']},
#                '智能交通': {
#                        'cities':['shanghai', 'shenzhen'],
#                        'webs':['liepin','zhilian','bosszhipin','indeed',],
#                        'title_red':['轨','车','规划'],
#                        'title_green':['交通'],
#                        'description_red':['轨','CAD','Auto'], 
#                        'description_green':['应届','究生','硕士']},
#                },
                '产品经理': {
                        'cities':['shenzhen'],
                        'webs':['linkedin'],
                        'title_red':['总监', '专员'],
#                        'title_green':['交通'],
                        'description_red':[], 
                        'description_green':[]},
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
    db = jobDataBase()
    # future todos: change the structure of cfgs, categories: global, bot, db, spider,
    
    while True:
        counter = 0
        while counter < crawls_per_day: 
            print('main: crawling sequence {}/{},\n'.format(counter + 1, crawls_per_day))
            t_start = time.time()
            current_pool = db.poolShow()
            agent = jobSpider(cfgs)
            captured = agent.scheduler(current_pool)
            db.insert(captured)
            
            t_crawl = int(time.time() - t_start)
            t_sleep = 86400/crawls_per_day - t_crawl + random.randint(-600, 600)
            t_sleep = t_sleep if t_sleep > 0 else 0
            print('main: Ok, Ich werde {} Stunde schalfen\n'.format(round(t_sleep/3600, 2)))
#            time.sleep(t_sleep)
            time.sleep(3) # for test
            counter += 1
        
        if db.poolCheck() > 2000:
            messager = tellMyBot(token, chat_id)
            messager.poolAlert(db.poolCheck())
        gc.collect()
        
        
if __name__ == '__main__':
    main(job_cfgs)

