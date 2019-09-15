# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 09:35:47 2019

@author: ert
"""

from local_var import chat_token, chat_id
from bot import tellMyBot
from job_db import jobDataBase
import time

def main():
    db = jobDataBase()
    messager = tellMyBot(chat_token, chat_id)
    new_jobs = db.fetchnew()
    print('call: Sending messages to bot...\n')
    messager.send2me(new_jobs)
    new_timestamp = int(time.strftime('%y%m%d%H%M',time.localtime(time.time())))
    db.addTimestamp(new_timestamp)
    print('call: Done!\n')
    
if __name__ == '__main__':
    main()
