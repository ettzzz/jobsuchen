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
        self.pool_table = 'pool'
        
        self.conn = sqlite3.connect(self.database)
        self.c = self.conn.cursor()
        self.initiate()
#        self.c.execute("PRAGMA table_info({})".format(table_name))
#        self.n_columns = len(self.c.fetchall())
        self.n_columns = 9
        
    def initiate(self):
        try:
            self.c.execute('CREATE TABLE {}(UID TEXT PRIMARY KEY NOT NULL);'.format(self.pool_table))
            self.conn.commit()
        except:
            pass
        
    def addTable(self, table_name):
        self.c.execute('CREATE TABLE {}(\
                        UID TEXT PRIMARY KEY NOT NULL,\
                        Source CHAR(20) NOT NULL,\
                        Position TEXT NOT NULL,\
                        Release CHAR(20) NOT NULL,\
                        Company TEXT NOT NULL,\
                        Location TEXT,\
                        Payment CHAR(20),\
                        URL TEXT NOT NULL,\
                        Keyword TEXT NOT NULL\
                        );'.format(table_name))
        self.conn.commit()
    
    def allTables(self):
        self.c.execute("SELECT name FROM sqlite_master WHERE TYPE='table' ORDER BY name")
        return self.c.fetchall()
    
    def newTables(self):
        pass

    def insert(self, table_name, captured_jobs):
        column_query = ('{},' * self.n_columns)[:-1]
        for each_job in captured_jobs:
            try:
                self.c.execute("INSERT INTO {} (UID) VALUES ('{}');".format(self.pool_table, each_job['URL']))
                self.c.execute("INSERT INTO {} ({}) VALUES {};".format(table_name, column_query.format(*each_job), tuple(each_job.values())))
                self.conn.commit()
            except:
                traceback.print_exc()
                continue
    
    def fetch(self, table_name):
        self.c.execute('SELECT * FROM {};'.format(table_name))
        return self.c.fetchall()
    
    def clean(self, table_name):
        self.c.execute("DELETE FROM {};".format(table_name))
        self.conn.commit()
        
    def reset(self):
        for each_table in self.allTables():
            self.c.execute("DROP TABLE {};".format(each_table[0]))
        self.conn.commit()
        
    def pool_check(self):
        self.c.execute("SELECT count(*) FROM {};".format(self.pool_table))
        return True if self.c.fetchall()[0][0] > 6000 else False
    
if __name__ == '__main__':
    test = jobDataBase()
