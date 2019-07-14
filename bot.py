#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 10:22:33 2019

@author: eriti
"""


import requests
import time

class tellMyBot():

    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_base = 'https://api.telegram.org/bot{}/sendMessage'.format(self.token)
        self.header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) \
          AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20'}

    def buildHtmlMessage(self, each_job): 
        try:
            title = each_job[1] + '|' + each_job[2] + '|' + each_job[3] + '|' + each_job[4] + '|' + each_job[5]
            # Source, Position, Release, Comapny, Location
            text = '<a href="{}">{}</a>'.format(each_job[7], title)
        except:
            text = 'HTML message Error'
        return text

    def send2me(self, all_jobs):
        if len(all_jobs) < 200:
            for each_job in all_jobs:
                bot_params = {
                        'chat_id': self.chat_id,
                        'text': self.build_html_message(each_job),
                        'disable_web_page_preview': 'True',
                        'parse_mode': 'HTML',
                        }
                requests.get(self.api_base, headers=self.header, params=bot_params)
                time.sleep(0.5)
        else:
            bot_params = {
                        'chat_id': self.chat_id,
                        'text': 'Just too many messages({}), I will just skip them this time.'.format(len(all_jobs)),
                        }
            requests.get(self.api_base, headers=self.header, params=bot_params)
            
    def poolAlert(self, pool_level):
        bot_params = {
                        'chat_id': self.chat_id,
                        'text': 'The pool level is exceeding the threshold! The current level is {}.'.format(pool_level),
                        }
        requests.get(self.api_base, headers=self.header, params=bot_params)
            
