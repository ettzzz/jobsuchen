#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 10:22:02 2019

@author: eriti
"""


import sqlite3
import traceback

class jobDataBase():
    
    def __init__(self):
        self.database = 'jobs.db'
        self.job_table = 'jobs'
        self.pool_table = 'pool'
        self.conn = sqlite3.connect(self.database)
        self.c = self.conn.cursor()
        self.initiate()
        self.c.execute("PRAGMA table_info({})".format(self.job_table))
        self.n_columns = len(self.c.fetchall())
        
    def initiate(self):
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
                            Keyword TEXT NOT NULL,\
                            Comment TEXT\
                            );'.format(self.job_table))
            self.conn.commit()
        except: # gebraucht or unexpected exit
            self.clean()

    def insert(self, true_job_list):
        homogenization = '{},' * self.n_columns
        homo = homogenization[:-1]
        
        for each_job in true_job_list:
            try:
                self.c.execute("INSERT INTO {} (UID) VALUES ('{}');".format(self.pool_table, each_job['UID']))
                self.c.execute(
                    "INSERT INTO {} ({}) VALUES {};".format(self.job_table, homo.format(*each_job), tuple(each_job.values()))
                    )
            except:
                print('job db has some problems \n')
                print(traceback.format_exc())
                continue
        self.conn.commit()
    
    def fetch(self):
        self.c.execute('SELECT * FROM {};'.format(self.job_table))
        return self.c.fetchall()
    
    def clean(self):
        self.c.execute("DELETE FROM {};".format(self.job_table))
        self.conn.commit()
        
    def reset(self):
        self.c.execute("DROP TABLE {};".format(self.job_table))
        self.c.execute("DROP TABLE {};".format(self.pool_table))
        self.conn.commit()
        
    def pool_check(self):
        self.c.execute("SELECT count(*) FROM {};".format(self.pool_table))
        return True if self.c.fetchall()[0][0] > 6000 else False
    
if __name__ == '__main__':
    test_db = jobDataBase()
