# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 08:34:50 2019

@author: ert
"""

import sys
import time
import random
import requests
import traceback
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote, unquote, urlsplit, parse_qs
from itertools import product
#from local_var import lkn_username, lkn_password


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
        
        self.targets = ['indeed', 'zhilian', 'liepin', 'lagou', 'bosszhipin']
#        self.targets = ['bosszhipin']
    
    def scheduler(self):
        self.browser_options = webdriver.firefox.options.Options()
        self.browser_options.add_argument('--headless')
        self.browser = webdriver.Firefox(executable_path = self.cfgs['global']['browser_path'], options = self.browser_options)
        self.browser.set_page_load_timeout(60)
        
        for job in list(self.cfgs['jobs'].keys()):
            for city in self.cfgs['global']['cities']:
                for target in self.targets:
                    eval("self.{}(self.cfgs['cities'][city][target], job)".format(target))
                
        filtered_jobs = []
        for i, each_job in enumerate(self.job_list):
            if self.filtering(each_job):
                filtered_jobs.append(each_job)
         
        self.spiderCheck()
        print('scheduler: {} captured, {} after filtering.\n'.format(len(self.job_list), len(filtered_jobs)))
        
        censored_jobs = []
        for i, each_job in enumerate(filtered_jobs):
            self.randomwait()
            if self.censoring(each_job):
                censored_jobs.append(each_job)
        print('scheduler: {} after censoring.\n'.format(len(censored_jobs)))
        self.browser.close()
        
        return censored_jobs


    def filtering(self, each_job):
        if each_job['URL'][:4] != 'http':
            return False
        elif any(each_verbot in each_job['Company'] for each_verbot in self.cfgs['filters']['company_stops']):
            return False
        elif any(each_verbot in each_job['Position'] for each_verbot in self.cfgs['filters']['position_stops']):
            return False
        elif any(each_verbot in each_job['Position'] for each_verbot in self.cfgs['jobs'][each_job['Keyword']]['title_red']):
            return False
        elif any(each_green not in each_job['Position'] for each_green in self.cfgs['jobs'][each_job['Keyword']]['title_green']):
            return False
        else:
            return True
    
    def censoring(self, each_job):
        try:
            censor_key = True
            if each_job['Source'] == 'lagou':
                self.browser.get(each_job['Comment']) #url4cookie
                self.browser.get(each_job['URL'])
                html = BeautifulSoup(self.browser.page_source, 'html.parser')
            else:
                r = requests.get(each_job['URL'], headers = eval(each_job['Comment']), timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
            
            d = html.select(self.description_css[each_job['Source']])[0].get_text().strip()
            
            if any(each_sw in d for each_sw in self.cfgs['jobs'][each_job['Keyword']]['description_red']):
                censor_key = False
            if any(each_gw in d for each_gw in self.cfgs['jobs'][each_job['Keyword']]['description_green']):
                print('Nah, green channel', each_job['Position'], each_job['URL'])
                censor_key = True
            return censor_key
        except:
            if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
            elif 'Timeout loading page after' in traceback.format_exc():
                print('censoring: timeout loading {}\n'.format(each_job['URL']))
                return True
            else:
                print('censoring bug: {}\n'.format(traceback.format_exc()))
                return False
    
    def linkedin(self, city, keyword): # linkedin has been temporarilly deprecated
            pages = self.crawl_size // 25 # 25 jobs/page 
            release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
            for each_page in range(pages):
                params = {
                    'f_JT': 'F', # full time job
                    'f_TP': 1,
#                    'f_TPR': 'r86400', # last 24 hr
#                    'f_LF': 'f_EA', # less than 10 candidates
                    'keywords': keyword,
                    'location': city['location'],
                    'locationId':city['locationId'],
                    'start': each_page * 25, 
                    'sortBy': 'DD',
                    }
                url4jobs = 'https://www.linkedin.com/jobs/search?' + urlencode(params)
                try:
                    self.browser.get(url4jobs)
                    self.randomwait()
                    html = BeautifulSoup(self.browser.page_source, 'html.parser')
                    jobs = html.select(self.html_css['linkedin'])
                    for each_job in jobs:
                        cache = {
                                'UID': str(each_job['data-id']),
                                'Source': 'linkedin',
                                'Position': each_job.select('span.screen-reader-text')[0].get_text().strip(),
                                'Release': release,
                                'Company': each_job.select('div > h4')[0].get_text().strip(),
                                'Location': each_job.select('div > span')[0].get_text().strip(),
                                'Payment': 'None',
                                'URL': 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'.format(each_job['data-id']),
                                'Keyword': keyword,
                                'Comment': str({'User-Agent':self.user_agent}),
                                }
                        self.job_list.append(cache)
                except:
                    if 'KeyboardInterrupt' in traceback.format_exc():
                        raise KeyboardInterrupt
                    else:
                        print('linkedin bug: {}\n'.format(traceback.format_exc()))
            
    def indeed(self, city, keyword): 
        pages = self.crawl_size // 50
        release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
        for each_page in range(pages):
            params = {
                    'as_and': keyword, # 包含所有关键字 
                    'jt': 'fulltime', # 工作类型 临时工什么的
                    'as_not':'实习',
#                    'as_src':'http%3A%2F%2Fmy.yingjiesheng.com',
                    'sr': '', # directhire过滤招聘中介
                    'radius': 50, # 位置半径km
                    'l': city,
                    'fromage': 1, # 1天前, 'any'为任何时间
                    'limit': 50, # jobs per page
                    'sort': 'date', # 排序方式
                    'psf': 'advsrch', # 搜索模式 advanced
                    'start': each_page * 50
                    }
            url4jobs = 'https://cn.indeed.com/%E5%B7%A5%E4%BD%9C?' + urlencode(params)
            try:
                r = requests.get(url4jobs, headers = {'User-Agent':self.user_agent}, timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select(self.html_css['indeed'])
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['id']),
                            'Source': 'indeed',
                            'Position': each_job.select('div.title')[0].get_text().strip(),
                            'Release': release,
                            'Company': each_job.select('span.company')[0].get_text().strip(),
                            'Location': each_job.select('span.location')[0].get_text().strip(),
                            'Payment': 'None',
                            'URL': 'https://cn.indeed.com' + each_job.select('div.title > a')[0]['href'],
                            'Keyword': keyword,
                            'Comment':str({'User-Agent':self.user_agent}),
                            }
                    self.job_list.append(cache)
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('indeed bug: {}\n'.format(traceback.format_exc()))
                    
    def liepin(self, city, keyword): 
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
            url4jobs = 'https://www.liepin.com/zhaopin?' + urlencode(params)
            try:
                r = requests.get(url4jobs, headers = {'User-Agent':self.user_agent}, timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select(self.html_css['liepin'])
                for each_job in jobs:
                    url = each_job.select('div.job-info > h3 > a')[0]['href']
                    if url[:3] == '/a/':
                        url = 'https://www.liepin.com' + url
                    cache = {
                            'UID': url.split('/')[-1][:-6],
                            'Source': 'liepin',
                            'Position': each_job.select('div.job-info > h3')[0].get_text().strip(),
                            'Release': each_job.select('div.job-info > p.time-info > time')[0]['title'][-6:], # '2019年05月09日'
                            'Company': each_job.select('p.company-name > a')[0].get_text().strip(),
                            'Location': each_job.select('div.job-info > p > .area')[0].get_text(),
                            'Payment': each_job.select('div.job-info > p > span')[0].get_text(),
                            'URL': url,
                            'Keyword': keyword,
                            'Comment': str({'User-Agent':self.user_agent}),
                            }
                    self.job_list.append(cache)
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('liepin bug: {}\n'.format(traceback.format_exc()))
            
        
    def zhilian(self, city, keyword): 
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
            url4cookie = 'https://sou.zhaopin.com?' + urlencode(params)
            params4jobs = {
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
            url4jobs = 'https://fe-api.zhaopin.com/c/i/sou?' + urlencode(params4jobs)
            headers4jobs = {
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://sou.zhaopin.com',
                'Referer': url4cookie,
                'User-Agent': self.user_agent,
                }
            try:
                self.browser.get(url4cookie)
                cookies = self.browser.get_cookies()
                s = requests.Session()
                for cookie in cookies:
                    s.cookies.set(cookie['name'], cookie['value'])
            except:
                print('zhilian bug: {}'.format(traceback.format_exc()))
                    
            try:
                r = requests.get(url4jobs, headers = headers4jobs, cookies = s.cookies, timeout = 10)
                jobs = r.json()['data']['results']
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['number']),
                            'Source': 'zhilian',
                            'Position': each_job['jobName'],
                            'Release': each_job['updateDate'].split(' ')[0][-5:],
                            'Company': each_job['company']['name'],
                            'Location': each_job['city']['display'],
                            'Payment': each_job['salary'],
                            'URL': each_job['positionURL'],
                            'Keyword': keyword,
                            'Comment': str(headers4jobs),
                            }
                    self.job_list.append(cache)
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('zhilian bug: {}\n'.format(traceback.format_exc()))

    def lagou(self, city, keyword): 
            pages = self.crawl_size // 15
            params4cookie = {
                'px':'new', # 排序
                'gx':'全职',
                'isSchoolJob':'1',
                'xl':'本科,硕士',
                'city':city,
                'labelWords':'',
                'fromSearch':'true',
                'suginput':'',
                }
            url4cookie = 'https://www.lagou.com/jobs/list_{}?{}'.format(quote(keyword),urlencode(params4cookie))
            params4jobs = {
                'city':city,
                'needAddtionalResult':'false',
                }
            url4jobs = 'https://www.lagou.com/jobs/positionAjax.json?' + urlencode(params4jobs)
            headers4jobs = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': url4cookie,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
                }
            try:
                s = requests.Session()
                s.get(url4cookie, headers = headers4jobs, timeout = 5)
                for each_page in range(pages):
                    data = {
                            'first': 'true' if each_page == 0 else 'false',
                            'pn': str(each_page+1),
                            'kd': keyword,}
                    r = requests.post(url4jobs, data = data, headers=headers4jobs, cookies=s.cookies, timeout = 10)
                    if '频繁' in r.text:
                        print('lagou got caught')
                    jobs = r.json()['content']['positionResult']['result']
                    for each_job in jobs:
                        cache = {
                                'UID': str(each_job['positionId']),
                                'Source': 'lagou',
                                'Position': each_job['positionName'],
                                'Release': each_job['createTime'].split(' ')[0][-5:],
                                'Company': each_job['companyFullName'],
                                'Location': each_job['city'] + ' ' + str(each_job['district']),
                                'Payment': each_job['salary'],
                                'URL': 'https://www.lagou.com/jobs/{}.html'.format(each_job['positionId']),
                                'Keyword': keyword,
                                'Comment': url4cookie,
                                } 
                        self.job_list.append(cache)
                    
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('lagou bug: {}\n'.format(traceback.format_exc()))
        
    def bosszhipin(self, city, keyword):
        pages = self.crawl_size // 30
        release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
        for each_page in range(pages):
            params4jobs = {
            'query': keyword,
            'city': city,
            'page': str(each_page),
#            'degree':'204', # master degree
            'experience':'104', # working experience
            }
            url4jobs = 'https://www.zhipin.com/job_detail?' + urlencode(params4jobs)
            
            try:
                url4cookie = 'https://www.zhipin.com/c{}-p{}/'.format(params4jobs['city'], 230204 + random.randint(-2, 6))
                self.browser.get(url4cookie)
                self.randomwait()
                cookies = self.browser.get_cookies()
                s = requests.Session()
                for cookie in cookies:
                    s.cookies.set(cookie['name'], cookie['value'])
                    
                headers4jobs = {
                    'User-Agent':self.user_agent,
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Host':'www.zhipin.com',
                    'X-Requested-With':'XMLHttpRequest',
                    'TE':'Trailers',}
            
                r = requests.get(url4jobs, headers = headers4jobs, cookies = s.cookies, timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs  = html.select(self.html_css['bosszhipin'])
                for each_job in jobs:
                    cache = {
                            'UID': each_job.select('h3.name > a')[0]['data-jid'],
                            'Source': 'bosszhipin',
                            'Position': each_job.select('div.job-title')[0].get_text().strip(),
                            'Release': release,
                            'Company': each_job.select('div.company-text > h3.name > a')[0].get_text().strip(),
                            'Location': each_job.select('div.info-primary > p')[0].get_text().strip(),
                            'Payment': each_job.select('span.red')[0].get_text().strip(),
                            'URL': 'https://www.zhipin.com{}'.format(each_job.select('h3.name > a')[0]['href']),
                            'Keyword': keyword,
                            'Comment': str(headers4jobs),
                            }
                    self.job_list.append(cache)
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('bosszhipin bug: {}\n'.format(traceback.format_exc()))

    
    def randomwait(self):
        sec = round(random.randint(1, 2) + random.uniform(0.5, 0.7), 2)
        time.sleep(sec)
        
    def spiderCheck(self):
        if len(self.job_list) != 0:
            ungenuegend = []
            ungenuegend.extend(self.targets)
            for each_source in self.targets:
                for i, each_job in enumerate(self.job_list):
                    if each_job['Source'] == each_source:
                        ungenuegend.remove(each_source)
                        break
            if len(ungenuegend) == 0:
                print('spiderCheck: Alles gut!\n')
            else:
                for i in ungenuegend:
                    print('spiderCheck: {} IS NOT OK!\n'.format(i))
        else: 
            print('spiderCheck: ERROR: THERE IS NO RECORD IN self.job_list.\n')
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
    from run_job import job_cfgs   
    test = jobSpider(job_cfgs)
    alles = test.scheduler()
    print(len(alles),len(test.job_list))
    

#    from local_var import token, chat_id
#    from bot import tellMyBot
#    alles2 = []
#    for i in alles:
#        alles2.append(list(i.values()))
#    bot = tellMyBot(token, chat_id)
#    bot.send2me(alles2)
