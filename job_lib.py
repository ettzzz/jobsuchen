#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 09:38:46 2019

@author: eriti
"""

def zhilian_cookie_factory(arg1):
    key_array = [15, 35, 29, 24, 33, 16, 1, 38, 10, 9, 19, 31, 40, 27, 22, 23,\
                 25, 13, 6, 11, 39, 18, 20, 8, 14, 21, 32, 26, 2, 30, 7, 4, 17,\
                 5, 3, 28, 34, 37, 12, 36]
    data = "3000176000856006061501533003690027800375"
    
    step1 = []
    for i in range(len(arg1)):
        for ii in range(len(key_array)):
            if key_array[ii] == i + 1:
                step1.append(ii)
    
    cache = ""
    for i in range(len(step1)):
        ii = step1.index(i)
        cache += arg1[ii]
    
    iii = 0
    cookie = ""
    while iii < len(cache) and iii < len(data):
        a = int(cache[iii:iii+2], 16)
        b = int(data[iii:iii+2], 16)
        c = hex(a ^ b)[2:]
        if len(c) == 1:
            c = '0' + c
        cookie += c
        iii += 2
    return cookie


job_cfgs = {
            'global':{
                    'user_id':'000',
                    'crawls_per_day':6,
                    'crawl_size':100,
                    'db_name': 'jobs.db',
                    },
            'filters':{
                'company_stops':['百度','baidu'],
                'position_stops':['实习','售','经理','高级','资深','总监','主管','专员','大数据'],
                },
            'jobs':{
                'python':{ # test
                        'cities':['shanghai'],
                        'webs':['lagou'],
                        'title_red':['后端','java'],
                        'title_green':['python'],
                        'description_red':['c++','hadoop','大专','专科'], 
                        'description_green':['应届','graduate',]
                        },
#                'python数据分析': {
#                        'cities':['shanghai'],
#                        'webs':['lagou', 'yingjiesheng','liepin','zhilian','bosszhipin',],
#                        'title_red':['后端','java','c++'],
#                        'title_green':['python','数据'],
#                        'description_red':['hadoop','docker','vue','大专','专科'], 
#                        'description_green':['应届','graduate',]
#                        },
#                '交通数据':{
#                        'cities':['shanghai'],
#                        'webs':['yingjiesheng','lagou','liepin','zhilian'],
#                        'title_red':['轨','规划','大'],
#                        'title_green':['交通'],
#                        'description_red':['轨','cad','auto'], 
#                        'description_green':['应届','硕士']
#                        },
#                '游戏数据':{
#                        'cities':['shanghai'],
#                        'webs':['yingjiesheng','lagou','zhilian','liepin'],
#                        'title_red':[],
#                        'title_green':['数据'],
#                        'description_red':[], 
#                        'description_green':['应届','python']
#                        },
#                'GIS':{
#                        'cities':['shanghai'],
#                        'webs':['yingjiesheng','lagou','indeed','zhilian','liepin','linkedin'],
#                        'title_red':['销售'],
#                        'title_green':['gis','数据','开发'],
#                        'description_red':['cad','auto'], 
#                        'description_green':['应届','硕士']
#                        },
#                
                },

        }
            




