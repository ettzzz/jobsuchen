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
from local_var import lkn_username, lkn_password


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
        self.targets = list(self.description_css.keys())

    def startBrowser(self):
        self.browser_options = webdriver.firefox.options.Options()
        self.browser_options.add_argument('--headless')
        self.browser_options.add_argument('--disable-gpu')
        self.browser = webdriver.Firefox(executable_path = self.cfgs['global']['browser_path'], \
                                         options = self.browser_options)
        self.set_page_load_timeout(30)
        
        if 'linkedin' in self.targets:
            self.browser.get('https://www.linkedin.com/login')
            self.browser.find_element_by_id('username').send_keys(lkn_username)
            self.browser.find_element_by_id('password').send_keys(lkn_password)
            self.browser.find_element_by_class_name('login__form_action_container ').click()
            self.randomwait()
            self.browser.get('https://www.linkedin.com/m/logout/')
    
    def scheduler(self):
        
        idxs = list(product(self.cfgs['global']['cities'], list(self.cfgs['jobs'].keys()), self.targets))
        
        self.startBrowser()
        
        for each_idx in idxs:
            city_name, keyword, source = each_idx
            city = self.cfgs['cities'][city_name][source]
            self.urls.extend(eval("self.{}('ersteURL', (city, keyword))".format(source)))
            
        for each_url in self.urls:
            self.randomwait(False)
            eval("self.{}('zweiteURL', each_url)".format(each_url['source']))
            
        self.spiderCheck()
        
        filtered_jobs = []
        for i, each_job in enumerate(self.job_list):
            if self.filtering(each_job):
                filtered_jobs.append(each_job)
            
        censored_jobs = []
        filtered_jobs = (random.sample(filtered_jobs,len(filtered_jobs)))
        previous_source = filtered_jobs[0]['Source']
        for i, each_job in enumerate(filtered_jobs):
            if previous_source == each_job['Source']:
                self.randomwait(False)
            else:
                previous_source = each_job['Source']
                self.randomwait(False)
                
            if self.censoring(each_job):
                censored_jobs.append(each_job)
            else:
                continue
        
        return censored_jobs


    def filtering(self, each_job):
        if each_job['URL'][:4] != 'http':
            return False
        elif any(each_verbot in each_job['Company'] for each_verbot in self.cfgs['filters']['company_stops']):
            return False
        elif any(each_verbot in each_job['Position'] for each_verbot in self.cfgs['filters']['position_stops']):
            return False
        else:
            return True
    
    def censoring(self, each_job):
        censor_key = True
        try:
            if each_job['Source'] == 'lagou':
                self.browser.get(each_job['Comment']) #url4cookie
                self.randomwait(long_wait = True)
                self.browser.get(each_job['URL'])
                html = BeautifulSoup(self.browser.page_source, 'html.parser')
            else:
                r = requests.get(each_job['URL'], headers = each_job['Comment'], timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
            
            d = html.select(self.description_css[each_job['Source']])[0].get_text().strip()
            if any(each_sw in d for each_sw in self.cfgs['jobs'][each_job['Keyword']]['stop']):
                censor_key = False
            if any(each_gw in d for each_gw in self.cfgs['jobs'][each_job['Keyword']]['go']):
                print('Nah, green channel', each_job['Position'], each_job['URL'])
                censor_key = True
        except:
            if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
            else:
                print('censoring bug: {}\n'.format(traceback.format_exc()))
            censor_key = False
        return censor_key
    
    def linkedin(self, category, _input):
        if category == 'ersteURL':
            city, keyword = _input
            urlsNheaders = []
            pages = self.crawl_size // 25 # 25 jobs/page 
            
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
                urlsNheaders.append({'source':'linkedin', 
                                     'url':url4jobs, 
                                     'headers':{'User-Agent':self.user_agent}, 
                                     'cookies':'',
                                     'keyword':keyword})
                
            return urlsNheaders
        elif category == 'zweiteURL':
            release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
            try:
                self.browser.get(_input['url'])
                html = BeautifulSoup(self.browser.page_source, 'html.parser')
                jobs = html.select(self.html_css[_input['source']])
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['data-id']),
                            'Source': _input['source'],
                            'Position': each_job.select('span.screen-reader-text')[0].get_text().strip(),
                            'Release': release,
                            'Company': each_job.select('div > h4')[0].get_text().strip(),
                            'Location': each_job.select('div > span')[0].get_text().strip(),
                            'Payment': 'None',
                            'URL': 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'.format(each_job['data-id']),
                            'Keyword': _input['keyword'],
                            'Comment': _input['headers'],
                            }
                    self.job_list.append(cache)
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('linkedin bug: {}\n'.format(traceback.format_exc()))
        else:
            print('linkedin: False category name.\n')
            
    def indeed(self, category, _input): 
        if category == 'ersteURL':
            urlsNheaders = []
            city, keyword = _input
            pages = self.crawl_size // 50
            for each_page in range(pages):
                params = {
                        'as_and': keyword, # 包含所有关键字 
                        'jt': 'fulltime', # 工作类型 临时工什么的
                        'as_not':'实习',
                        'as_src':'http%3A%2F%2Fmy.yingjiesheng.com',
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
                urlsNheaders.append({'source':'indeed', 
                                     'url':url4jobs, 
                                     'headers':{'User-Agent':self.user_agent}, 
                                     'keyword':keyword})
                
            return urlsNheaders
        elif category == 'zweiteURL':
            release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
            try:
                r = requests.get(_input['url'], headers = _input['headers'], timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select(self.html_css[_input['source']])
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['id']),
                            'Source': _input['source'],
                            'Position': each_job.select('div.title')[0].get_text().strip(),
                            'Release': release,
                            'Company': each_job.select('span.company')[0].get_text().strip(),
                            'Location': each_job.select('span.location')[0].get_text().strip(),
                            'Payment': 'None',
                            'URL': 'https://cn.indeed.com' + each_job.select('div.title > a')[0]['href'],
                            'Keyword': _input['keyword'],
                            'Comment': _input['headers'],
                            }
                    self.job_list.append(cache)
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('indeed bug: {}\n'.format(traceback.format_exc()))
        else:
            print('indeed: False category name.\n')
        
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
                url4jobs = 'https://www.liepin.com/zhaopin?' + urlencode(params)
                urlsNheaders.append({'source':'liepin', 
                                     'url':url4jobs, 
                                     'headers':{'User-Agent':self.user_agent}, 
                                     'keyword':keyword})
                
            return urlsNheaders
        elif category == 'zweiteURL':
            try:
                r = requests.get(_input['url'], headers = _input['headers'], timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select(self.html_css[_input['source']])
                for each_job in jobs:
                    url = each_job.select('div.job-info > h3 > a')[0]['href']
                    if url[:3] == '/a/':
                        url = 'https://www.liepin.com' + url
                    cache = {
                            'UID': url.split('/')[-1][:-6],
                            'Source': _input['source'],
                            'Position': each_job.select('div.job-info > h3')[0].get_text().strip(),
                            'Release': each_job.select('div.job-info > p.time-info > time')[0]['title'][-6:], # '2019年05月09日'
                            'Company': each_job.select('p.company-name > a')[0].get_text().strip(),
                            'Location': each_job.select('div.job-info > p > .area')[0].get_text(),
                            'Payment': each_job.select('div.job-info > p > span')[0].get_text(),
                            'URL': url,
                            'Keyword': _input['keyword'],
                            'Comment': _input['headers'],
                            }
                    self.job_list.append(cache)
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('liepin bug: {}\n'.format(traceback.format_exc()))
        else:
            print('liepin: False category name.\n')
            
        
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
                headers = {
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
                    urlsNheaders.append({'source':'zhilian', 
                                         'url':url4jobs, 
                                         'headers':headers,
                                         'cookies':s.cookies,
                                         'keyword':keyword})
                except:
                    print('zhilian bug: {}'.format(traceback.format_exc()))
                    
            return urlsNheaders
        elif category == 'zweiteURL':
            try:
                r = requests.get(_input['url'], headers = _input['headers'], cookies = _input['cookies'], timeout = 10)
                jobs = r.json()['data']['results']
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['number']),
                            'Source': _input['source'],
                            'Position': each_job['jobName'],
                            'Release': each_job['updateDate'].split(' ')[0][-5:],
                            'Company': each_job['company']['name'],
                            'Location': each_job['city']['display'],
                            'Payment': each_job['salary'],
                            'URL': each_job['positionURL'],
                            'Keyword': _input['keyword'],
                            'Comment': _input['headers'],
                            }
                    self.job_list.append(cache)
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('zhilian bug: {}\n'.format(traceback.format_exc()))
        else:
            print('zhilian: False category name.\n')

    def lagou(self, category, _input): 
        if category == 'ersteURL':
            urlsNheaders = []
            city, keyword = _input
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
                'Host': 'www.lagou.com',
                'X-Anit-Forge-Code':'0',	
                'X-Anit-Forge-Token':'None',	
                'X-Requested-With':'XMLHttpRequest',
                }
            try:
                self.browser.get(url4cookie)
                cookies = self.browser.get_cookies()
                s = requests.Session()
                for cookie in cookies:
                    s.cookies.set(cookie['name'], cookie['value'])
            
                for each_page in range(pages):
                    data = {
                            'first': 'true' if each_page == 0 else 'false',
                            'pn': str(each_page+1),
                            'kd': keyword,
                            }
                    urlsNheaders.append({'source':'lagou', 
                                         'url':url4jobs, 
                                         'headers':headers4jobs, 
                                         'cookies':s.cookies, 
                                         'data':data, 
                                         'keyword':keyword})
            except:
                print('lagou bug: {}\n'.format(traceback.format_exc()))
                
            return urlsNheaders
        elif category == 'zweiteURL':
            try:
                r = requests.post(_input['url'], data=_input['data'], headers=_input['headers'], cookies=_input['cookies'], timeout = 10)
                if '频繁' in r.text:
                    print('lagou got caught')
                jobs = r.json()['content']['positionResult']['result']
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['positionId']),
                            'Source': _input['source'],
                            'Position': each_job['positionName'],
                            'Release': each_job['createTime'].split(' ')[0][-5:],
                            'Company': each_job['companyFullName'],
                            'Location': each_job['city'] + ' ' + str(each_job['district']),
                            'Payment': each_job['salary'],
                            'URL': 'https://www.lagou.com/jobs/{}.html'.format(each_job['positionId']),
                            'Keyword': _input['keyword'],
                            'Comment': _input['headers']['Referer'],
                            } 
                    self.job_list.append(cache)
                    
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('lagou bug: {}\n'.format(traceback.format_exc()))
        else:
            print('lagou: False category name.\n')
        
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
#                'degree':'204', # master degree
                'experience':'104', # working experience
                }
                
                url4jobs = 'https://www.zhipin.com/job_detail?' + urlencode(params)
                url4cookie = 'https://www.zhipin.com/c{}-p{}/'.format(params['city'], 230204 + random.randint(-2, 2))
                
                try:
                    self.browser.get(url4cookie)
                    cookies = self.browser.get_cookies()
                    s = requests.Session()
                    for cookie in cookies:
                        s.cookies.set(cookie['name'], cookie['value'])
                        
                    headers4jobs = {
                    'User-Agent':self.user_agent,
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Host':'www.zhipin.com',
                    'X-Requested-With':'XMLHttpRequest',
                    'TE':'Trailers',
                    }
                    urlsNheaders.append({'source':'bosszhipin', 
                                         'url':url4jobs, 
                                         'headers':headers4jobs, 
                                         'cookies':s.cookies, 
                                         'keyword':keyword})
                except:
                    print('bosszhipin bug: {}\n'.format(traceback.format_exc()))
            return urlsNheaders
        
        elif category == 'zweiteURL':
            release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
            try:
                r = requests.get(_input['url'], headers = _input['headers'], cookies = _input['cookies'],timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs  = html.select(self.html_css[_input['source']])
                for each_job in jobs:
                    cache = {
                            'UID': each_job.select('h3.name > a')[0]['data-jid'],
                            'Source': _input['source'],
                            'Position': each_job.select('div.job-title')[0].get_text().strip(),
                            'Release': release,
                            'Company': each_job.select('div.company-text > h3.name > a')[0].get_text().strip(),
                            'Location': each_job.select('div.info-primary > p')[0].get_text().strip(),
                            'Payment': each_job.select('span.red')[0].get_text().strip(),
                            'URL': 'https://www.zhipin.com{}'.format(each_job.select('h3.name > a')[0]['href']),
                            'Keyword': _input['keyword'],
                            'Comment': _input['headers'],
                            }
                    self.job_list.append(cache)
            except:
                if 'KeyboardInterrupt' in traceback.format_exc():
                    raise KeyboardInterrupt
                else:
                    print('bosszhipin bug: {}\n'.format(traceback.format_exc()))
        else:
            print('bosszhipin: False category name.\n')
        
    
    def randomwait(self, long_wait = True):
        if long_wait == True:
            sec = round(random.randint(1, 2) + random.uniform(0.5, 0.7), 2)
        else:
            sec = round(random.uniform(0.3, 0.5), 2)
#        print('I\'m waiting for {} seconds'.format(sec))
        time.sleep(sec)
        
    def spiderCheck(self):
        if len(self.job_list) != 0:
            for each_source in list(self.description_css.keys()):
                for i, each_job in enumerate(self.job_list):
                    if each_job['Source'] == each_source:
                        print('spiderCheck: {} is ok.\n'.format(each_source))
                        break
            print('spiderCheck: There are {} captured job before filtering.\n'.format(len(self.job_list)))
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
    alles = []
    test = jobSpider(job_cfgs)
    alles.extend(test.scheduler())
#    ori = test.job_list
#    urls = test.urls
#    print(len(alles),len(ori))
    
        
    

