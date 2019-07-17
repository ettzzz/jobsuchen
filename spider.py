# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 08:34:50 2019

@author: ert
"""

import sys
import traceback
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote
from itertools import product


class jobSpider():
    
    def __init__(self, cfgs):
        self.cfgs = cfgs
        self.crawl_size = self.cfgs['global']['crawl_size']
        self.job_list = []
        self.urls = []
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'
        self.description_css = {
                'linkedin':'section.description',
                'indeed':'#jobDescriptionText',
                'zhilian':'div.describtion > div.describtion__detail-content',
                'liepin':'div.content.content-word',
                'lagou':'dl#job_detail.job_detail > dd.job_bt',
                'bosszhipin':'div.detail-content > div.job-sec > div.text',
                }
        self.html_css = {
                'linkedin':'ul.jobs-search__results-list > li',
                'indeed':'div[data-tn-component]',
                'zhilian':'',
                'liepin':'ul.sojob-list > li',
                'lagou':'',
                'bosszhipin':'#main > div > div.job-list > ul > li',
                }
        
    def scheduler(self, fast = False):
        comps = list(product(self.cfgs['global']['cities'], list(self.cfgs['jobs'].keys()), list(self.description_css.keys())))
#        comps = list(product(self.cfgs['global']['cities'], list(self.cfgs['jobs'].keys()),['bosszhipin']))
        for each_comp in comps:
            self.urls.extend(self.URLBuilder(each_comp))
            
        self.urls = random.sample(self.urls,len(self.urls))
        previous_source = self.urls[0]['source']
        for each_url in self.urls:
#            if previous_source == each_url['source']:
#                self.randomwait()
#            else:
#                previous_source = each_url['source']
            self.URLParser(each_url)
        
        self.spiderCheck()
        
        filtered = []
        for i, each_job in enumerate(self.job_list):
            if self.filtering(each_job):
                filtered.append(each_job)
            
        if fast == False:
            censored = []
            filtered = (random.sample(filtered,len(filtered)))
            previous_job = filtered[0]['Source']
            for i, each_job in enumerate(filtered):
                if previous_job == each_job['Source']:
                    self.randomwait()
                else:
                    previous_job = each_job['Source']
                if self.censoring(each_job):
                    censored.append(each_job)
            
            return censored
        else:
            return filtered
    
    def URLBuilder(self, component):
        city_name, keyword, source = component
        city = self.cfgs['cities'][city_name][source]
        return eval("self.{}('ersteURL', (city, keyword))".format(source))
    
    def URLParser(self, url_dict):
        eval("self.{}('zweiteURL', url_dict)".format(url_dict['source']))
        
    def filtering(self, each_job):
        if each_job['URL'][:4] != 'http':
            return False
        elif any(each_verbot in each_job['Company'] for each_verbot in self.cfgs['filters']['company_stops']):
            return False
        elif any(each_verbot in each_job['Position'] for each_verbot in self.cfgs['filters']['position_stops']):
            return False
        elif each_job['Keyword'][1:] not in each_job['Position']:
            return False
        else:
            return True
    
    def censoring(self, each_job):
        censor_key = True
        for i, each_url in enumerate(random.sample(self.urls, len(self.urls))):
            if each_url['source'] == each_job['Source']:
                headers = each_url['headers']
                break
            else:
                headers = {'User-Agent':self.user_agent}

        try:
            if each_job['Source'] == 'lagou':
                url_start = each_job['Comment']
                s = requests.Session()
                s.get(url_start, headers = headers)
                r = requests.get(each_job['URL'], headers = headers, cookies = s.cookies, timeout = 10)
            else:
                r = requests.get(each_job['URL'], headers = headers, timeout = 10)
            
            html = BeautifulSoup(r.text, 'html.parser')
            d = html.select(self.description_css[each_job['Source']])[0]
                
            if any(each_sw in d for each_sw in self.cfgs['jobs'][each_job['Keyword']]['stop']):
                print('Bingo gotcha bitch')
                censor_key = False
            if any(each_gw in d for each_gw in self.cfgs['jobs'][each_job['Keyword']]['go']):
                print('Nah, green channal')
                censor_key = True
        except:
            
            exc_type, exc_value, exc_tb = sys.exc_info()
            if 'KeyboardInterrupt' in str(exc_type):
                    raise KeyboardInterrupt
            func_name = sys._getframe().f_code.co_name,
            print('{}: {} Requests/CSS bug with {} / {} at {}.\n'.format(func_name, each_job['Source'], exc_value, exc_type, each_job['URL']))
        return censor_key
    
    def linkedin(self, category, _input):
        if category == 'ersteURL':
            urlsNheaders = []
            city, keyword = _input
            pages = self.crawl_size // 25 # 25 jobs/page 
            for each_page in range(pages):
                params = {
                    'f_JT': 'F', # full time job
                    'f_TPR': 'r86400', # last 24 hr
                    'f_LF': 'f_EA', # less than 10 candidates
                    'keywords': keyword,
                    'locationId': city, 
                    'start': each_page * 25, 
                    'sortBy': 'DD',
                    }
                url_parse = 'https://www.linkedin.com/jobs/search' + '?' + urlencode(params)
                headers = {'User-Agent':self.user_agent}
                urlsNheaders.append({'source':'linkedin', 'url':url_parse, 'headers':headers, 'keyword':keyword})
            return urlsNheaders
        elif category == 'zweiteURL':
            url_parse = _input['url']
            headers = _input['headers']
            source = _input['source']
            keyword = _input['keyword']
            release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
            try:
                r = requests.get(url_parse.replace('ERSATZ', '%'), headers = headers,  timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select(self.html_css[source])
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['data-id']),
                            'Source': source,
                            'Position': each_job.select('span.screen-reader-text')[0].get_text().strip(),
                            'Release': release,
                            'Company': each_job.select('div > h4')[0].get_text().strip(),
                            'Location': each_job.select('div > span')[0].get_text().strip(),
                            'Payment': 'None',
                            'URL': 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'.format(each_job['data-id']),
                            'Keyword': keyword,
                            'Comment': 'None'
                            }
                    self.job_list.append(cache)
            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                if 'KeyboardInterrupt' in str(exc_type):
                    raise KeyboardInterrupt
                func_name = sys._getframe().f_code.co_name,
                print('{}: Requests/CSS bug with {} / {}.\n'.format(func_name, exc_value, exc_type))
        else:
            print('{}: False category name.\n'.format(sys._getframe().f_code.co_name))
            
    def indeed(self, category, _input): 
        if category == 'ersteURL':
            urlsNheaders = []
            city, keyword = _input
            pages = self.crawl_size // 50
            for each_page in range(pages):
                params = {
                        'as_and': keyword, # 包含所有关键字 
                        'jt': 'fulltime', # 工作类型 临时工什么的
                        'sr': 'directhire', # 过滤招聘中介
                        'radius': 50, # 位置半径km
                        'l': city,
                        'fromage': 3, # 3天前
                        'limit': 50, # jobs per page
                        'sort': 'date', # 排序方式
                        'psf': 'advsrch', # 搜索模式 advanced
                        'start': each_page * 50
                        }
                url_parse = 'https://cn.indeed.com/%E5%B7%A5%E4%BD%9C' + '?' + urlencode(params)
                headers = {'User-Agent':self.user_agent}
                urlsNheaders.append({'source':'indeed', 'url':url_parse, 'headers':headers, 'keyword':keyword})
            return urlsNheaders
        elif category == 'zweiteURL':
            url_parse = _input['url']
            headers = _input['headers']
            source = _input['source']
            keyword = _input['keyword']
            release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
            try:
                r = requests.get(url_parse, headers = headers, timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select(self.html_css[source])
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['id']),
                            'Source': source,
                            'Position': each_job.select('div.title')[0].get_text().strip(),
                            'Release': release,
                            'Company': each_job.select('span.company')[0].get_text().strip(),
                            'Location': each_job.select('span.location')[0].get_text().strip(),
                            'Payment': 'None',
                            'URL': 'https://cn.indeed.com' + each_job.select('div.title > a')[0]['href'],
                            'Keyword': keyword,
                            'Comment': 'None',
                            }
                    self.job_list.append(cache)
            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                if 'KeyboardInterrupt' in str(exc_type):
                    raise KeyboardInterrupt
                func_name = sys._getframe().f_code.co_name,
                print('{}: Requests/CSS bug with {} / {}.\n'.format(func_name, exc_value, exc_type))
        else:
            print('{}: False category name.\n'.format(sys._getframe().f_code.co_name))
        
    def liepin(self, category, _input): 
        if category == 'ersteURL':
            urlsNheaders = []
            city, keyword = _input
            pages = self.crawl_size // 40
            for each_page in range(pages):
                params = {"init":"-1",
                          "searchType":"1",
                          "headckid":"3b90473e084fa596",
                          "dqs":city,
                          "pubTime":"3",
                          "compkind":'', #"010", # foreign companies
                          "fromSearchBtn":"2",
                          "ckid":"7bfc0aebc74f03a6",
                          "degradeFlag":"0",
                          "key":keyword,
                          "siTag":"ZFDYQyfloRvvhTxLnVV_Qg~5uaOfDEtJdSczgdCly3x8A",
                          "d_sfrom":"search_prime",
                          "d_ckId":"37532abf95b160ab64a582ccf0d7efaf",
                          "d_curPage":str(0 if each_page == 0 else each_page - 1),
                          "d_pageSize":"40",
                          "d_headId":"37532abf95b160ab64a582ccf0d7efaf",
                          "curPage":str(each_page)}
                url_parse = 'https://www.liepin.com/zhaopin?' + urlencode(params)
                headers = {'User-Agent':self.user_agent}
                urlsNheaders.append({'source':'liepin', 'url':url_parse, 'headers':headers, 'keyword':keyword})
            return urlsNheaders
        elif category == 'zweiteURL':
            url_parse = _input['url']
            headers = _input['headers']
            source = _input['source']
            keyword = _input['keyword']
            try:
                r = requests.get(url_parse, headers = headers, timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select(self.html_css[source])
                for each_job in jobs:
                    url = each_job.select('div.job-info > h3 > a')[0]['href']
                    if url[:3] == '/a/':
                        url = 'https://www.liepin.com' + url
                    cache = {
                            'UID': str(each_job.select('div.job-info > h3 > a')[0]['href'].split('/')[-1][:-6]),
                            'Source': source,
                            'Position': each_job.select('div.job-info > h3')[0].get_text().strip(),
                            'Release': each_job.select('div.job-info > p > time')[0]['title'][-6:], # '2019年05月09日'
                            'Company': each_job.select('p.company-name > a')[0].get_text().strip(),
                            'Location': each_job.select('div.job-info > p > .area')[0].get_text(),
                            'Payment': each_job.select('div.job-info > p > span')[0].get_text(),
                            'URL': url,
                            'Keyword': keyword,
                            'Comment': 'None',
                            }
                    self.job_list.append(cache)
            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                if 'KeyboardInterrupt' in str(exc_type):
                    raise KeyboardInterrupt
                func_name = sys._getframe().f_code.co_name,
                print('{}: Requests/CSS bug with {} / {}.\n'.format(func_name, exc_value, exc_type))
        else:
            print('{}: False category name.\n'.format(sys._getframe().f_code.co_name))
        
        
    def zhilian(self, category, _input): 
        if category == 'ersteURL':
            urlsNheaders = []
            city, keyword = _input
            pages = self.crawl_size // 90
            for each_page in range(pages):
                params = {
                     'jl': city,
                     'ct': '0', 
                     'kw': keyword,
                     'kt': '3',
                     'sf': '0',
                     'st': '0',
                     'et': '2', 
                     'el': '4', 
                     'p': str(each_page+1)
                     }
                url_start = 'https://sou.zhaopin.com?{}'.format(urlencode(params))
                
                params_parse = {
                    "pageSize":"90",
                    "start": str(each_page*90),
                    "cityId":city,
                    "salary":"0,0",
                    "workExperience":"-1",
                    "education":"4", # bachelor degree = 4# master degree = 3
                    "companyType":"-1", # foreign companies = 2
                    "employmentType":"2", 
                    "jobWelfareTag":"-1",
                    "kw":keyword,
                    "kt":"3",
                    "_v":"0.71357600",
                    "x-zp-page-request-id":"72d284de0afe4ce6a6a662736a5145e2-{}-{}".format(int(1000*time.time()), random.randint(0,1000000))
                    }
                url_parse = 'https://fe-api.zhaopin.com/c/i/sou?' + urlencode(params_parse)
                headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Origin': 'https://sou.zhaopin.com',
                    'Referer': url_start,
                    'User-Agent': self.user_agent,
                    }
                urlsNheaders.append({'source':'zhilian', 'url':url_parse, 'headers':headers, 'keyword':keyword})
            return urlsNheaders
        elif category == 'zweiteURL':
            url_parse = _input['url']
            headers = _input['headers']
            source = _input['source']
            keyword = _input['keyword']
            try:
                r = requests.get(url_parse, headers = headers, timeout = 10)
                jobs = r.json()['data']['results']
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['number']),
                            'Source': source,
                            'Position': each_job['jobName'],
                            'Release': each_job['updateDate'].split(' ')[0][-5:],
                            'Company': each_job['company']['name'],
                            'Location': each_job['city']['display'],
                            'Payment': each_job['salary'],
                            'URL': each_job['positionURL'],
                            'Keyword': keyword,
                            'Comment': 'None',
                            }
                    self.job_list.append(cache)
            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                if 'KeyboardInterrupt' in str(exc_type):
                    raise KeyboardInterrupt
                func_name = sys._getframe().f_code.co_name,
                print('{}: Requests/CSS bug with {} / {}.\n'.format(func_name, exc_value, exc_type))
        else:
            print('{}: False category name.\n'.format(sys._getframe().f_code.co_name))

    def lagou(self, category, _input): 
        if category == 'ersteURL':
            urlsNheaders = []
            city, keyword = _input
            pages = self.crawl_size // 15
            params_start = {
                'px':'new', # 排序
                'gx':'全职',
                'isSchoolJob':'1',
                'xl':'本科,硕士',
                'city':city,
                'labelWords':'',
                'fromSearch':'True',
                'suginput':'',
                }
            url_start = 'https://www.lagou.com/jobs/list_{}?{}'.format(quote(keyword),urlencode(params_start))
            params_parse = {
                'city':city,
                'needAddtionalResult':'false',
                }
            url_parse = 'https://www.lagou.com/jobs/positionAjax.json?' + urlencode(params_parse)
            headers_parse = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': url_start,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
                'Host': 'www.lagou.com',
                'X-Anit-Forge-Code':'0',	
                'X-Anit-Forge-Token':'None',	
                'X-Requested-With':'XMLHttpRequest',
                }
            
            for each_page in range(pages):
                data = {
                        'first': 'true' if each_page == 0 else 'false',
                        'pn': str(each_page+1),
                        'kd': keyword,
                        }
                s = requests.Session()
                try:
                    s.get(url_start, headers = headers_parse, timeout = 10)
                    urlsNheaders.append({'source':'lagou', 'url':url_parse, 'url_start':url_start, \
                                         'headers':headers_parse, 'cookies':s.cookies, 'data':data, 'keyword':keyword})
                except:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    if 'KeyboardInterrupt' in str(exc_type):
                        raise KeyboardInterrupt
                    func_name = sys._getframe().f_code.co_name,
                    print('{}: Session bug with {} / {}.\n'.format(func_name, exc_value, exc_type))
                
            return urlsNheaders
        elif category == 'zweiteURL':
            url_parse = _input['url']
            url_start = _input['url_start']
            headers = _input['headers']
            source = _input['source']
            cookies = _input['cookies']
            data = _input['data']
            keyword = _input['keyword']
            
            try:
                r = requests.post(url_parse, data=data, headers=headers, cookies=cookies, timeout = 10)
                jobs = r.json()['content']['positionResult']['result']
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['positionId']),
                            'Source': source,
                            'Position': each_job['positionName'],
                            'Release': each_job['createTime'].split(' ')[0][-5:],
                            'Company': each_job['companyFullName'],
                            'Location': each_job['city'] + ' ' + str(each_job['district']),
                            'Payment': each_job['salary'],
                            'URL': 'https://www.lagou.com/jobs/{}.html'.format(each_job['positionId']),
                            'Keyword': keyword,
                            'Comment': url_start,
                            } 
                    self.job_list.append(cache)
                    
            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                if 'KeyboardInterrupt' in str(exc_type):
                    raise KeyboardInterrupt
                func_name = sys._getframe().f_code.co_name,
                print('{}: Requests/CSS bug with {} / {}.\n'.format(func_name, exc_value, exc_type))
                print(r.json())
        else:
            print('{}: False category name.\n'.format(sys._getframe().f_code.co_name))
        
    def bosszhipin(self, category, _input):
        if category == 'ersteURL':
            urlsNheaders = []
            city, keyword = _input
            pages = self.crawl_size // 30
            
            s = requests.Session()
            for each_page in range(pages):
                params = {
                'query': keyword,
                'city': city,
                'page': str(each_page),
#                    'degree':'204', # master degree
#                    'experience':'103', # working experience
                }
                headers_parse = {
                'User-Agent':self.user_agent,
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Host':'www.zhipin.com',
                'Referer': 'https://www.zhipin.com/',
                'X-Requested-With':'XMLHttpRequest'
                }
                url_parse = 'https://www.zhipin.com/job_detail?' + urlencode(params)
                try:
                    s.get(url_parse, headers = headers_parse, timeout = 10, proxies = self.proxies())
                    urlsNheaders.append({'source':'bosszhipin', 'url':url_parse, 'headers':headers_parse, 'cookies':s.cookies, 'keyword':keyword})
                except:
                    exc_type, exc_value, exc_tb = sys.exc_info()
                    if 'KeyboardInterrupt' in str(exc_type):
                        raise KeyboardInterrupt
                    func_name = sys._getframe().f_code.co_name,
                    print('{}: Session bug with {} / {}'.format(func_name, exc_value, exc_type))
            
            return urlsNheaders
        
        elif category == 'zweiteURL':
            url_parse = _input['url']
            headers = _input['headers']
            source = _input['source']
            cookies = _input['cookies']
            keyword = _input['keyword']
            release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
            try:
                r = requests.get(url_parse, headers = headers, cookies = cookies, proxies = self.proxies(), timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs  = html.select(self.html_css[source])
                for each_job in jobs:
                    cache = {
                            'UID': each_job.select('h3.name > a')[0]['data-jid'],
                            'Source': source,
                            'Position': each_job.select('div.job-title')[0].get_text().strip(),
                            'Release': release,
                            'Company': each_job.select('div.company-text > h3.name > a')[0].get_text().strip(),
                            'Location': each_job.select('div.info-primary > p')[0].get_text().strip(),
                            'Payment': each_job.select('span.red')[0].get_text().strip(),
                            'URL': 'https://www.zhipin.com{}'.format(each_job.select('h3.name > a')[0]['href']),
                            'Keyword': keyword,
                            'Comment': 'None',
                            }
                    self.job_list.append(cache)
            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                if 'KeyboardInterrupt' in str(exc_type):
                    raise KeyboardInterrupt
                func_name = sys._getframe().f_code.co_name,
                print('{}: Requests/CSS bug with {} / {}.\n'.format(func_name, exc_value, exc_type))
        else:
            print('{}: False category name.\n'.format(sys._getframe().f_code.co_name))
        
    
    def randomwait(self):
        sec = round(random.randint(3,5) + random.uniform(-1,1), 2)
        time.sleep(sec)
        
    def spiderCheck(self):
        if len(self.job_list) != 0:
            for each_source in list(self.description_css.keys()):
                for each_job in self.job_list:
                    if each_job['Source'] == each_source:
                        print('{}: {} is ok.\n'.format(sys._getframe().f_code.co_name, each_source))
                        break
            print('{}: There are {} captured job before filtering.\n'.format(sys._getframe().f_code.co_name, len(self.job_list)))
        else:
            print('{}: ERROR: THERE IS NO RECORD IN self.job_list.\n'.format(sys._getframe().f_code.co_name))
            sys.exit()
            
    def proxies(self):
        proxies = None
        counter = 0
        while counter < 5:
            p = requests.get('http://134.209.199.241/proxy/get', timeout = 3)
            if p.text[:4] == 'http':
                proxies = {'http':p.text, 'https':p.text} 
                try: 
                    r = requests.get('https://www.baidu.com', headers = {'User-Agent':self.user_agent}, timeout = 5)
                    if r.status_code == 200:
                        break
                    else:
                        continue
                except:
                    continue
            counter += 1
        return proxies
    
            
if __name__ == "__main__":
    job_cfgs = {
            'global':{
                    'crawls_per_day':3,
                    'crawl_size':100,
                    'db_name': 'Arbeitsuchen.db',
                    'jtable_name':'Arbeiten',
                    'ptable_name':'Bad',
                    'ctable_name':'Staedte',
                    'cities':['beijing'],
                    },
            'jobs':{
#                'python后端': {'stop':['++','adoop',], 'go':['应届','quirement','raduate']},
                'python': {'stop':[ '++','crapy','ava'], 'go':['应届','quirement','raduate']},
                '智能交通': {'stop':['轨道','CAD','Auto'], 'go':['应届','海外',]},
#                '交通工程': {'stop':['抗压','轨道','CAD','Auto'], 'go':['应届','海外',]},
#                '智慧交通': {'stop':['轨道','CAD','Auto'], 'go':['应届','海外',]},
                },
            'filters':{
                'company_stops':['轨道','百度','aidu'],
                'position_stops':['轨道','汽车','实习','售','经理','高级','资深','总监','ava','++',],
                },
            'cities':{
                'beijing':{
                            'linkedin':'cnERSATZ3A8911',
                            'indeed':'北京',
                            'liepin':'010',
                            'zhilian':'530',
                            'lagou':'北京',
                            'bosszhipin':'101010100'
                            },
                },
            }
    test = jobSpider(job_cfgs)
    for each_keyword in list(test.cfgs['jobs'].keys()):
        filtered = test.scheduler()
    ori = test.job_list
    urls = test.urls
    print(len(ori))
    

