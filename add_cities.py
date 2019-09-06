
from job_db import jobDataBase
from job_lib import job_cfgs as cfgs
temp = jobDataBase(user_id = cfgs['global']['user_id'])

cities = []

'''
somehow we scrape some city-pinyin-code pairs
as form of pinyin, web, codename
'''

cities = [('hangzhou', 'lagou', '杭州'), ('hangzhou', 'bosszhipin', '101210100'), ('hangzhou', 'linkedin', 'cn:8931'),
('hangzhou', 'zhilian', '653'), ('hangzhou', 'liepin', '070020'), ('hangzhou', 'indeed', '杭州'), ('hangzhou', 'yingjiesheng', '2102')]

for i in cities:
    temp.insertCityset(i[0], i[1], i[2])