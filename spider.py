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
from urllib.parse import urlencode, quote


class jobSpider():
    
    def __init__(self, cfgs):
        self.crawl_size = 100
        self.job_list = []
        self.cfgs = cfgs
        self.user_agents = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
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
        self.company_stops = ['某','一线',]
        self.position_stops = ['实习','销售','经理','高级','Java','C++','java','c++',]
        self.cities = {
                'shanghai':{'linkedin':'shanghai','indeed':'上海','liepin':'020','zhilian':'538','lagou':'上海','bosszhipin':'101020100'},
                'beijing':{'linkedin':'beijing','indeed':'北京','liepin':'010','zhilian':'530','lagou':'北京', 'bosszhipin':'101010100'},
                }
        self.censor_css = {
                'linkedin':'section.description',
                'indeed':'#jobDescriptionText > div > div > div',
                'zhilian':'div.describtion > div.describtion__detail-content',
                'liepin':'div.content.content-word',
                'lagou':'div.job-detail',
                'bosszhipin':'div.detail-content > div.job-sec > h3 > div.text',
                'yingjie':None,
                }



    def linkedin(self, keyword, city):
        url_parse = 'https://cn.linkedin.com/jobs/search/'
        pages = self.crawl_size // 25 # 25 jobs/page 
        headers = {'User-Agent':random.choice(self.user_agents)}
        release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
        
        for each_page in range(pages):
            params = {
                'f_JT': 'F', # foreign companies only
                'f_TPR': 'r86400',
                'keywords': keyword,
                'location': city, 
                'start': each_page * 25, 
                'sortBy': 'DD',
                }
            try:
                r = requests.get(url_parse, headers = headers, params = params, timeout = 10)
                time.sleep(5)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select('a[data-job-id]') # tag a with attribute data-job-id # or html.find_all(name = 'li', attrs = {'class':'jobs-search-result-item'})
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['data-job-id']),
                            'Source': 'linkedin',
                            'Position': each_job.select('div > h3')[0].get_text().strip(),
                            'Release': release,
                            'Company': each_job.select('div > h4')[0].get_text().strip(),
                            'Location': each_job.select('div > p')[0].get_text().strip(),
                            'Payment': 'None',
                            'URL': 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'.format(each_job['data-job-id']),
                            'Keyword': keyword,
                            }
                    self.job_list.append(cache)
            except:
#                print('request error with status_code {} at {}.'.format(r.status_code, r.url))
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
    #                'as_not': None, # 不包含这些关键字 
#                    'as_ttl': keyword, # 职位名称中包含词语 
    #                'as_cmp': None, # 从这个公司
                    'jt': 'all', # 工作类型 临时工什么的
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
                r = requests.get(url_parse, headers = headers, params = params, timeout = 10)
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
                            }
                    self.job_list.append(cache)
            except:
#                print('request error with status_code {} at {}.'.format(r.status_code, r.url))
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
                      "compkind":"010", # foreign companies
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
                r = requests.get(url_parse, headers = headers, params = params, timeout = 10)
                html = BeautifulSoup(r.text, 'html.parser')
                jobs = html.select('ul.sojob-list > li')
                for each_job in jobs:
                    try:
                        url = each_job.select('div.job-info > h3 > a')[0]['href']
                        if url[:3] == '/a/':
                            url = 'https://www.liepin.com' + url
                        else:
                            pass
                        cache = {
                                'UID': str(each_job.select('div.job-info > h3 > a')[0]['href'].split('/')[-1][:-6]),
                                'Source': 'liepin',
                                'Position': each_job.select('div.job-info > h3')[0].get_text().strip(),
                                'Release': each_job.select('div.job-info > p > time')[0]['title'][-6:], # '2019年05月09日'
                                'Company': each_job.select('p.company-name > a')[0].get_text().strip(),
                                'Location': each_job.select('div.job-info > p > a.area')[0].get_text(),
                                'Payment': each_job.select('div.job-info > p > span')[0].get_text(),
                                'URL': url,
                                'Keyword': keyword,
                                }
                        self.job_list.append(cache)
                    except:
                        continue
            except:
#                print('request error with status_code {} at {}.'.format(r.status_code, r.url))
                continue

    
    def zhilian(self, keyword, city): 
        pages = self.crawl_size // 90
        url_parse = 'https://fe-api.zhaopin.com/c/i/sou'
        
        for each_page in range(pages):
            params = {
                 'jl': city,
                 'ct': '2', # foreign companies
                 'kw': keyword,
                 'kt': '3',
                 'sf': '0',
                 'st': '0',
                 'et': '2', # full-time job
                 'el': '3', # master degree
                 'p': str(each_page+1)
                     }
            url_start = 'https://sou.zhaopin.com?' + urlencode(params)
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
                "education":"-1",
                "companyType":"2",
                "employmentType":"-1",
                "jobWelfareTag":"-1",
                "kw":keyword,
                "kt":"3",
                "_v":"0.71357600",
                "x-zp-page-request-id":"72d284de0afe4ce6a6a662736a5145e2-{}-{}".format(int(1000*time.time()), random.randint(0,1000000))
            }
            try:
                r = requests.get(url_parse, headers = headers, params = params_parse, timeout = 10)
                time.sleep(5)
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
                            }
                    self.job_list.append(cache)
            except:
#                print('request error with status_code {} at {}.'.format(r.status_code, r.url))
                continue
    
    
    
    def lagou(self, keyword, city): 
        pages = self.crawl_size // 15
        
        url_start = 'https://www.lagou.com/jobs/list_{}?labelWords=&fromSearch=true&suginput='.format(quote(keyword))
        url_parse = 'https://www.lagou.com/jobs/positionAjax.json?city={}&needAddtionalResult=false'.format(city)
        headers_parse = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': url_start,
                'Cache-Control': 'keep-alive',
                'Content-Length': '25',
                'Content-Type': 'application/x-www.form.urlencoded; charset=UTF-8',
                'User-Agent': random.choice(self.user_agents),
                'Host': 'www.lagou.com',
                }
        headers_start = {
                'Accept': 'application/json, text/javascript, */*',
                'Referer': url_start,
                'User-Agent': random.choice(self.user_agents),
                }
        s = requests.Session()
        s.get(url_start, headers = headers_start)
        cookies = s.cookies  
        for each_page in range(pages):
            first_page = 'true' if each_page == 0 else 'false'
            data = {
                    'first': first_page,
                    'pn': str(each_page+1),
                    'kd': keyword,
                    }
            try:
                r = s.post(url_parse, data=data, headers=headers_parse, cookies=cookies, timeout=15)
                time.sleep(5)
                jobs = r.json()['content']['positionResult']['result']
                for each_job in jobs:
                    cache = {
                            'UID': str(each_job['positionId']),
                            'Source': 'lagou',
                            'Position': each_job['positionName'],
                            'Release': each_job['createTime'].split(' ')[0][-5:],
                            'Company': each_job['companyFullName'],
                            'Location': each_job['city'] + ' ' + each_job['district'],
                            'Payment': each_job['salary'],
                            'URL': 'https://www.lagou.com/jobs/{}.html'.format(each_job['positionId']),
                            'Keyword': keyword,
                            }
                    self.job_list.append(cache)
            except:
#                print('request error with status_code {} at {}.'.format(r.status_code, r.url))
                continue   

    def bosszhipin(self, keyword, city):
        pages = self.crawl_size // 30
        url_parse = 'https://www.zhipin.com/job_detail/'
        headers = {'User-Agent':random.choice(self.user_agents)}
        release = '自动日期' + time.strftime('%m-%d',time.localtime(time.time()))
        
        for each_page in range(pages):
            params = {
                'query': keyword,
                'city': city,
                'page': str(each_page),
#                'degree':'204', # master degree
#                'experience':'103', # working experience
                }
            
            try:
                r = requests.get(url_parse, headers = headers, params = params, timeout = 10)
                time.sleep(5)
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
                            }
                    self.job_list.append(cache)
            except:
                continue   

    
    def yingjie(self, keyword, city):
        pass
    
    
    def filtering(self, each_job, fast = True):
        if each_job['URL'][:5] != 'https':
#            print('wryyyyyyyyyy URL Falsch', each_job['URL'],each_job['Source'])
            return False
        elif any(each_verbot in each_job['Position'] for each_verbot in self.position_stops):
#            print('wryyyyyyyyyy Position Verbot', each_job['Position'], each_job['URL'])
            return False
        elif any(each_verbot in each_job['Company'] for each_verbot in self.company_stops):
#            print('wryyyyyyyyyy Company Verbot', each_job['Company'])
            return False
        elif each_job['Keyword'][1:] not in each_job['Position']:
            return self.censoring(each_job) if fast == False else False
#            if fast == False:
#                return self.censoring(each_job)
#            else:
#                print('wryyyyyyyyyy Keyword nicht in dem Position', each_job['Position'], each_job['Keyword'])
#                return False
        else:
            return True

                
    def censoring(self, each_job):
        try:
            headers = {'User-Agent':random.choice(self.user_agents)}
            r = requests.get(each_job['URL'], headers = headers, timeout = 10)
            html = BeautifulSoup(r.text, 'html.parser')
            d = html.select(self.cencor_css[each_job['Source']])[0]
            
            if any(each_sw in d for each_sw in self.cfgs[each_job['Keyword']]['stop']):
#                print('wryyyyyyyyyy Description Verbot', d)
                return False
            elif any(each_gw in d for each_gw in self.cfgs[each_job['Keyword']]['go']):
#                print('wryyyyyyyyyy Description green channel', d)
                return True
            else:
                return True
        except:
            return False

    
    def scheduler(self, keyword, fast = True):
        self.job_list = []
        filtered_job_list = []
        
        for each_city in self.cities.items():  
            self.linkedin(keyword, each_city[1]['linkedin'])
            self.indeed(keyword, each_city[1]['indeed'])
            self.liepin(keyword, each_city[1]['liepin'])
            self.zhilian(keyword, each_city[1]['zhilian'])
            self.lagou(keyword, each_city[1]['lagou'])
            self.bosszhipin(keyword, each_city[1]['bosszhipin'])
            
        for i, each_job in enumerate(random.sample(self.job_list,len(self.job_list))):
            if self.filtering(each_job, fast):
                filtered_job_list.append(each_job)
            else:
                pass
            
        return filtered_job_list
    
#from urllib.parse import urlparse, parse_qsl, 
#o = urlparse(url)
#q = dict(parse_qsl(o.query)) # or parse_qs(o.query)
#r.encoding('gbk')
#response = requests.request("GET", url, headers=headers, params=querystring)
if __name__ == "__main__":
    job_cfgs = {
        'python': {'stop':['弹性','大专' ], 'go':['应届','海外','硕士','quirement']},
#        '智能交通': {'stop':['弹性','轨道','大专'], 'go':['应届','海外','硕士']},
        }
    bot = jobSpider(job_cfgs)
    bot.linkedin('交通','shanghai')
    bot.lagou('交通','上海')
#    filtered = bot.scheduler('python',False)
    ori = bot.job_list

