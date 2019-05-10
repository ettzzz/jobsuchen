#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 10:22:02 2019

@author: eriti
"""

'''
Based on SQLite
(UID,Source:Position,Release,Company,Location,Payment,URL,Keyword)
'''

import sqlite3

class jobDB():
    
    def __init__(self):
        self.database = 'jobs.db'
        self.job_table = 'jobs'
        self.pool_table = 'pool'
        self.conn = sqlite3.connect(self.database)
        self.c = self.conn.cursor()
        self.prepare()
        
    def prepare(self):
        try:
            self.c.execute('CREATE TABLE {}(UID TEXT PRIMARY KEY NOT NULL);'.format(self.pool_table))
            self.c.execute('CREATE TABLE {}(\
                            UID TEXT PRIMARY KEY NOT NULL,\
                            Source CHAR(20) NOT NULL,\
                            Position TEXT NOT NULL,\
                            Release CHAR(20) NOT NULL,\
                            Company TEXT NOT NULL,\
                            Location TEXT,\
                            Payment CHAR(20),\
                            URL TEXT NOT NULL,\
                            Keyword TEXT NOT NULL);'.format(self.job_table))
            self.conn.commit()
        except: # gebraucht
            self.clean()

    def insert(self, true_job_list):
        for each_job in true_job_list:
            self.c.execute("SELECT count(*) FROM {} WHERE UID == '{}';".format(self.pool_table, each_job['UID']))
            if self.c.fetchone()[0] == 0:
                self.c.execute("INSERT INTO {} (UID) VALUES ('{}');".format(self.pool_table, each_job['UID']))
                self.c.execute(
                    "INSERT INTO {} (UID,Source,Position,Release,Company,Location,Payment,URL,Keyword) \
                     VALUES {};".format(self.job_table, tuple(each_job.values()))
                    )
            else:
                pass
        self.conn.commit()
    
    def fetch(self):
        self.c.execute('SELECT * FROM {};'.format(self.job_table))
        return self.c.fetchall()
    
    def clean(self):
        self.c.execute("DELETE FROM {};".format(self.job_table))
        self.conn.commit()
#        self.conn.close()
        
    def reset(self):
        self.c.execute("DROP TABLE {};".format(self.job_table))
        self.c.execute("DROP TABLE {};".format(self.pool_table))
        self.conn.commit()
        
    def pool_level(self):
        self.c.execute("SELECT count(*) FROM {};".format(self.pool_table))
        return self.c.fetchall()[0]

    def pool_check(self):
        return True if self.pool_level() > 6000 else False
    

