#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 10:22:19 2019

@author: eriti
"""


import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote, unquote
import traceback
#from job_debug import jobDebug


class jobSpider():
    
    def __init__(self, cfgs):
        
        self.crawl_size = 100
        self.job_list = []
        self.cfgs = cfgs
        self.user_agents = [
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
            ]
        self.description_css = {
                'linkedin':'section.description',
                'indeed':'#jobDescriptionText',
                'zhilian':'div.describtion > div.describtion__detail-content',
                'liepin':'div.content.content-word',
                'lagou':'dl#job_detail.job_detail > dd.job_bt > div.job-detail',
                'bosszhipin':'div.detail-content > div.job-sec > div.text',
                'yingjie':None,
                }
        
    def scheduler(self, keyword):
        
        self.job_list = []
        filtered_job_list = []
        
        for each_city in [*self.cfgs['cities']]:  
            self.linkedin(keyword, self.cfgs['cities'][each_city]['linkedin'])
            self.indeed(keyword, self.cfgs['cities'][each_city]['indeed'])
            self.liepin(keyword, self.cfgs['cities'][each_city]['liepin'])
            self.zhilian(keyword, self.cfgs['cities'][each_city]['zhilian'])
#            self.lagou(keyword, self.cfgs['cities'][each_city]['lagou'])
            self.bosszhipin(keyword, self.cfgs['cities'][each_city]['bosszhipin'])
            
        for i, each_job in enumerate(random.sample(self.job_list,len(self.job_list))):
            if self.filtering(each_job) and self.censoring(each_job):
                filtered_job_list.append(each_job)
            
        return filtered_job_list

    def proxies(self):
    
        proxies = None
        try:
            p = requests.get('http://www.ettzzz.me/proxy/get', timeout = 2)
            if p.text[:4] == 'http':
                proxies = {'http':p.text, 'https':p.text}
        except:
#            print('Fail to ask for a proxy. It\'s either timeout or no proxies available')
            pass
        return proxies
    
    
    def randomwait(self):
        return random.randint(3,5) + random.uniform(-1,1)


    def filtering(self, each_job):
        
        if each_job['URL'][:4] != 'http':
#            print('wryyyyyyyyyy URL Falsch', each_job['URL'],each_job['Source'])
            return False
        elif any(each_verbot in each_job['Company'] for each_verbot in self.cfgs['filters']['company_stops']):
#            print('wryyyyyyyyyy Company Verbot', each_job['Company'])
            return False
        elif any(each_verbot in each_job['Position'] for each_verbot in self.cfgs['filters']['position_stops']):
#            print('wryyyyyyyyyy Position Verbot', each_job['Position'], each_job['URL'])
            return False
        else:
            return True

                
    def censoring(self, each_job):
        
        censor_key = True
        headers = {'User-Agent':random.choice(self.user_agents)}

        try:
            r = requests.get(each_job['URL'], headers = headers, proxies = self.proxies(), timeout = 15)
            time.sleep(self.randomwait())
            html = BeautifulSoup(r.text, 'html.parser')
            d = html.select(self.description_css[each_job['Source']])[0]
                
            if any(each_sw in d for each_sw in self.cfgs['jobs'][each_job['Keyword']]['stop']):
                print('wryyyyyyyyyy Description Verbot', d)
                censor_key = False
            if any(each_gw in d for each_gw in self.cfgs['jobs'][each_job['Keyword']]['go']):
                print('wryyyyyyyyyy Description green channel', d)
                censor_key = True
                
        except Exception as e:
            if 'list index out of range' in traceback.print_exc():
                print('Possible css selector error at {} of {}.\n'.format(each_job['URL'], each_job['Source']))
            elif 'timeout' in traceback.print_exc():
                print('Timeout error at {} of {}.\n'.format(each_job['URL'], each_job['Source']))
            else:
                print('Some other errors as below.\n')
                print(traceback.print_exc() + '\n')
            censor_key = False
        
        return censor_key


    def linkedin(self, keyword, city):
        
        pages = self.crawl_size // 25 # 25 jobs/page 
        headers = {'User-Agent':random.choice(self.user_agents)}
        release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
        
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
            try:
                url_parse = 'https://www.linkedin.com/jobs/search' + '?' + urlencode(params)
                r = requests.get(url_parse.replace('ERSATZ', '%'), headers = headers, proxies = self.proxies(), timeout = 15)
                time.sleep(self.randomwait())
                html = BeautifulSoup(r.text, 'html.parser')
#                jobs = html.select('a[data-job-id]') # tag a with attribute data-job-id 
#                jobs = html.find_all(name = 'li', attrs = {'class':'jobs-search-result-item'})
                jobs = html.select('ul.jobs-search__results-list > li')

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
                            'Comment': 'None'
                            }
                    self.job_list.append(cache)
            except:
                print('Spider error of linkedin as below.\n {}\n'.format(traceback.print_exc()))
                continue
            
            
    def indeed(self, keyword, city): 
        
        url_parse = 'https://cn.indeed.com/%E5%B7%A5%E4%BD%9C'
        pages = self.crawl_size // 50
        headers = {'User-Agent':random.choice(self.user_agents)}
        release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
        
        for each_page in range(pages):
            params = {
                    'as_and': keyword, # 包含所有关键字 
    #                'as_phr': None, # 包含特定词语 
    #                'as_any': None, # 包含这些关键字
#                    'as_not': None, # 不包含这些关键字 
#                    'as_ttl': keyword, # 职位名称中包含词语 
    #                'as_cmp': None, # 从这个公司
                    'jt': 'fulltime', # 工作类型 临时工什么的
    #                'st': None, # 在以下网站搜索
                    'sr': 'directhire', # 过滤招聘中介
    #                'as_src': None, # 从这个求职网站
                    'radius': 50, # 位置半径km
                    'l': city,
                    'fromage': 3, # 3天前
                    'limit': 50, # jobs per page
                    'sort': 'date', # 排序方式
                    'psf': 'advsrch', # 搜索模式 advanced
                    'start': each_page * 50
                    }
            try:
                r = requests.get(url_parse, headers = headers, params = params, proxies = self.proxies(), timeout = 15)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select('div[data-tn-component]')
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
                            'Comment': 'None',
                            }
                    self.job_list.append(cache)
            except:
                print('Spider error of indeed as below.\n {}\n'.format(traceback.print_exc()))
                continue
    
    
    def liepin(self, keyword, city): 
        
        url_parse = 'https://www.liepin.com/zhaopin/'
        pages = self.crawl_size // 40
        headers = {'User-Agent':random.choice(self.user_agents)}
        
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
            try:
                r = requests.get(url_parse, headers = headers, params = params, proxies = self.proxies(), timeout = 15)
                time.sleep(self.randomwait())
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select('ul.sojob-list > li')
                for each_job in jobs:
                    url = each_job.select('div.job-info > h3 > a')[0]['href']
                    if url[:3] == '/a/':
                        url = 'https://www.liepin.com' + url
                    cache = {
                            'UID': str(each_job.select('div.job-info > h3 > a')[0]['href'].split('/')[-1][:-6]),
                            'Source': 'liepin',
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
                print('Spider error of liepin as below.\n {}\n'.format(traceback.print_exc()))
                continue

    
    def zhilian(self, keyword, city): 
        
        pages = self.crawl_size // 90
        url_parse = 'https://fe-api.zhaopin.com/c/i/sou'
        
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
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://sou.zhaopin.com',
                'Referer': url_start,
                'User-Agent': random.choice(self.user_agents),
                    }
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
            try:
                r = requests.get(url_parse, headers = headers, params = params_parse, proxies = self.proxies(), timeout = 15)
                time.sleep(self.randomwait())
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
                            'Comment': 'None',
                            }
                    self.job_list.append(cache)
            except:
                print('Spider error of zhilian as below.\n {}\n'.format(traceback.print_exc()))
                continue
    
    
    def lagou(self, keyword, city): 
        pages = self.crawl_size // 15
        url_base = 'https://www.lagou.com/jobs'
        
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
        params_parse = {
                'city':city,
                'needAddtionalResult':'false',
                }
        
        url_start = '{}/list_{}?{}'.format(url_base, quote(keyword),urlencode(params_start))
        url_parse = '{}/positionAjax.json?{}'.format(url_base, urlencode(params_parse))
        
        headers_parse = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': url_start,
                'User-Agent': random.choice(self.user_agents),
                'Host': 'www.lagou.com',
                'X-Anit-Forge-Code':'0',	
                'X-Anit-Forge-Token':'None',	
                'X-Requested-With':'XMLHttpRequest',
                }
        
        s = requests.Session()
        s.get(url_start, headers = headers_parse, proxies = self.proxies(), timeout = 10)
        for each_page in range(pages):
            first_page = 'true' if each_page == 0 else 'false'
            data = {
                    'first': first_page,
                    'pn': str(each_page+1),
                    'kd': keyword,
                    }
            try:
                r = s.post(url_parse, data=data, headers=headers_parse, cookies=s.cookies, proxies = self.proxies(), timeout=15)
                time.sleep(self.randomwait())
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
                            'Comment': 'None',
                            } 
                    self.job_list.append(cache)
            except Exception as e:
                print(traceback.format_exc())
                continue   


    def bosszhipin(self, keyword, city):
        
        pages = self.crawl_size // 30
        url_parse = 'https://www.zhipin.com/job_detail'
        release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
        timestamp = int(time.time()) - 1
        headers_start = {
                'User-Agent':random.choice(self.user_agents),
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Caceh-Control':'max-age=0',
                'Connection':'keep-alive',
                'Cookie':'lastCity=101010100; __c={}; __g=-;\
                        __l=l=%2Fwww.zhipin.com%2F&r=https%3A%2F%2Fwww.google.com%2F;\
                        __a=83361331.{}..{}.14.1.14.14; \
                        Hm_lvt_194df3105ad7148dcf2b98a91b5e727a={}; \
                        Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a={}; \
                        _uab_collina=156301810358065089864524'.format(timestamp, timestamp, timestamp, timestamp, timestamp + 789),
                'Host':'www.zhipin.com',
                'Referer': 'https://www.zhipin.com/',
                'TE': 'Trailers',
                'X-Requested-With':'XMLHttpRequest'
                }
        
        s = requests.Session()
        s.get('https://www.zhipin.com/', headers = headers_start, proxies = self.proxies(), timeout = 15)
        
        for each_page in range(pages):
            params = {
                'query': keyword,
                'city': city,
                'page': str(each_page),
#                'degree':'204', # master degree
#                'experience':'103', # working experience
                }
            headers_parse = {
                'User-Agent':random.choice(self.user_agents),
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'Caceh-Control':'max-age=0',
                'Connection':'keep-alive',
                'Cookie':'lastCity=101010100; __c={}; __g=-;\
                        __l=l=%2Fwww.zhipin.com%2F&r=https%3A%2F%2Fwww.google.com%2F;\
                        __a=83361331.{}..{}.14.1.14.14; \
                        Hm_lvt_194df3105ad7148dcf2b98a91b5e727a={}; \
                        Hm_lpvt_194df3105ad7148dcf2b98a91b5e727a={}; \
                        _uab_collina=156301810358065089864524'.format(timestamp, timestamp, timestamp, timestamp, timestamp + 789),
                'Host':'www.zhipin.com',
                'Referer': url_parse + '?' + urlencode(params),
                'TE': 'Trailers',
                'X-Requested-With':'XMLHttpRequest'
                }
            try:
                r = requests.get(url_parse, headers = headers_parse, params = params, cookies = s.cookies, proxies = self.proxies(), timeout = 15)
                time.sleep(self.randomwait())
                if '异常' in r.text:
                    # terminate? must send an alert
                    print('You got caught by bosszhipin \n')
                    continue
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select('#main > div > div.job-list > ul > li')
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
                            'Comment': 'None',
                            }
                    self.job_list.append(cache)
            except:
                print('Spider error of bosszhipin as below.\n {}\n'.format(traceback.print_exc()))
                continue   

    
    def yingjie(self, keyword, city):
        pass
#from urllib.parse import urlparse, parse_qsl, 
#o = urlparse(url)
#q = dict(parse_qsl(o.query)) # or parse_qs(o.query)
#r.encoding('gbk')
#response = requests.request("GET", url, headers=headers, params=querystring)

if __name__ == "__main__":
    job_cfgs = {
                'jobs':
                    {
                    'python后端': {'stop':['弹性','大专' ], 'go':['应届','海外','硕士','quirement']},
                    },
                'filters':
                    {
                    'company_stops':['某','一线','知名'],
                    'position_stops':['实习','销售','经理','高级','ava','++',],
                    },
                'cities':
                    {
                    'beijing':{
                                'linkedin':'beijing',
                                'indeed':'北京',
                                'liepin':'010',
                                'zhilian':'530',
                                'lagou':'北京',
                                'bosszhipin':'101010100'
                                },
                    },
                }
                    
    bot = jobSpider(job_cfgs)
#    bot.lagou('python后端', '北京')
    filtered = bot.scheduler('python后端')
    ori = bot.job_list
    print(len(ori))
    print(len(filtered))
#    
#    tmp = []
#    counter = 0
#    for i in ori:
#        if i['Source'] == 'bosszhipin':
#            tmp.append(i)
#
#    headers = {'User-Agent':"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"}
#    for each_job in tmp:        
#        r = requests.get(each_job['URL'], headers = headers, timeout = 15)
#        time.sleep(random.randint(3,5))
#        html = BeautifulSoup(r.text, 'html.parser')
#        d = html.select('div.detail-content > div.job-sec > div.text')[0]
#        
#    each_job = tmp[0]
