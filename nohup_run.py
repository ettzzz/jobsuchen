import time
import random
import gc
from itertools import product
import imp

import job_lib



def main2(cfgs):
    from job_db import jobDataBase
    from bot import tellMyBot
    from spider import jobSpider
    from local_var import chat_token, chat_id
    
    db = jobDataBase(user_id = cfgs['global']['user_id'])
    tasks = []
    for job in list(cfgs['jobs'].keys()):
        tasks.extend(i for i in product([job], cfgs['jobs'][job]['cities'], cfgs['jobs'][job]['webs']))
    task_cmds = list(map(lambda x: "self.{}('{}', '{}')".format(x[-1], db.getCityCode(x[1], x[-1]), x[0]), tasks))  
    
    current_pool = db.poolShow()
    agent = jobSpider(cfgs)
    captured = agent.scheduler(current_pool, task_cmds)
    db.insert(captured)
    
    if db.poolCheck() > 2000:
        messager = tellMyBot(chat_token, chat_id)
        messager.poolAlert(db.poolCheck())
    gc.collect()
    
    
    

if __name__ == '__main__':
    while True:
        imp.reload(job_lib)
        job_cfgs = job_lib.job_cfgs
        t_start = time.time()
        crawls_per_day = job_cfgs['global']['crawls_per_day']
        counter = 0
    
        main2(job_cfgs)
    
        t_crawl = int(time.time() - t_start)
        t_sleep = 86400/crawls_per_day - t_crawl + random.randint(-600, 600)
        t_sleep = t_sleep if t_sleep > 0 else 0
        print('main: Ok, Ich werde {} Stunde schalfen\n'.format(round(t_sleep/3600, 2)))
        time.sleep(t_sleep)
        time.sleep(3) # for test
        




