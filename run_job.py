#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 09:38:46 2019

@author: eriti
"""


import time
import random
import gc
from itertools import product

from job_db import jobDataBase
from bot import tellMyBot
from spider import jobSpider
from local_var import chat_token, chat_id

job_cfgs = {
            'global':{
                    'user_id':'000',
                    'crawls_per_day':6,
                    'crawl_size':100,
                    'db_name': 'jobs.db',
                    },
            'filters':{
                'company_stops':['百度','aidu'],
                'position_stops':['实习','售','经理','高级','资深','总监','主管','专员','银行',],
                },
            'jobs':{
                'python数据': {
                        'cities':['shanghai'],
                        'webs':['lagou','indeed','yingjiesheng','liepin','zhilian','bosszhipin',],
                        'title_red':['后端','ava','++'],
                        'title_green':['ython','数据'],
                        'description_red':['++','adoop','ocker','Vue','大专','专科'], 
                        'description_green':['应届','raduate',]},
                '智能交通': {
                        'cities':['shanghai'],
                        'webs':['liepin','zhilian','indeed','yingjiesheng'],
                        'title_red':['轨','车','规划'],
                        'title_green':['交通'],
                        'description_red':['轨','CAD','Auto'], 
                        'description_green':['应届','究生','硕士']},
                '交通数据':{
                        'cities':['shanghai'],
                        'webs':['yingjiesheng','lagou','indeed'],
                        'title_red':['轨','规划'],
                        'title_green':['交通'],
                        'description_red':['轨','CAD','Auto'], 
                        'description_green':['应届','究生','硕士']},
                },
            }


def main(cfgs):
    crawls_per_day = cfgs['global']['crawls_per_day']
    db = jobDataBase(user_id = cfgs['global']['user_id'])
    tasks = []
    for job in list(cfgs['jobs'].keys()):
        tasks.extend(i for i in product([job], cfgs['jobs'][job]['cities'], cfgs['jobs'][job]['webs']))
    task_cmds = list(map(lambda x: "self.{}('{}', '{}')".format(x[-1], db.getCityCode(x[1], x[-1]), x[0]), tasks))  
    
    while True:
        counter = 0
        while counter < crawls_per_day: 
            print('main: crawling sequence {}/{},\n'.format(counter + 1, crawls_per_day))
            t_start = time.time()
            
            current_pool = db.poolShow()
            agent = jobSpider(cfgs)
            captured = agent.scheduler(current_pool, task_cmds)
            db.insert(captured)
            
            t_crawl = int(time.time() - t_start)
            t_sleep = 86400/crawls_per_day - t_crawl + random.randint(-600, 600)
            t_sleep = t_sleep if t_sleep > 0 else 0
            print('main: Ok, Ich werde {} Stunde schalfen\n'.format(round(t_sleep/3600, 2)))
            time.sleep(t_sleep)
            time.sleep(3) # for test
            counter += 1
        
        if db.poolCheck() > 2000:
            messager = tellMyBot(chat_token, chat_id)
            messager.poolAlert(db.poolCheck())
        gc.collect()
        
        
if __name__ == '__main__':
    main(job_cfgs)

