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
        self.city_table = 'cityset'
        self.buildPool()
        self.buildCityset()
#        c.execute("PRAGMA table_info({})".format(table_name))
#        self.n_columns = len(c.fetchall())
        self.n_columns = 10
        
    def db_switch_on(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        return conn, c
    
    def buildPool(self):
        tables = self.allTables()
        conn, c = self.db_switch_on()
        if (self.pool_table,) not in tables:
            c.execute('CREATE TABLE {}(UID TEXT PRIMARY KEY NOT NULL);'.format(self.pool_table))
            conn.commit()
        else:
            pass
        c.close()
        conn.close()
        
    def buildCityset(self):
        tables = self.allTables()
        conn, c = self.db_switch_on()
        if (self.city_table,) not in tables:
            c.execute('CREATE TABLE {}(\
                      UID INTEGER PRIMARY KEY AUTOINCREMENT,\
                      pinyin TEXT NOT NULL,\
                      linkedin TEXT,\
                      indeed TEXT,\
                      zhilian TEXT,\
                      liepin TEXT,\
                      lagou TEXT,\
                      bosszhipin TEXT);'.format(self.pool_table))
            conn.commit()
        else:
            pass
        c.close()
        conn.close()
        
    def addTable(self, table_name):
        conn, c = self.db_switch_on()
        c.execute('CREATE TABLE {}(\
                        UID TEXT PRIMARY KEY NOT NULL,\
                        Source CHAR(20) NOT NULL,\
                        Position TEXT NOT NULL,\
                        Release CHAR(20) NOT NULL,\
                        Company TEXT NOT NULL,\
                        Location TEXT,\
                        Payment CHAR(20),\
                        URL TEXT NOT NULL,\
                        Keyword TEXT NOT NULL,\
                        Comment TEXT NOT NULL\
                        );'.format(table_name))
        conn.commit()
        c.close()
        conn.close()
    
    def allTables(self):
        conn, c = self.db_switch_on()
        c.execute("SELECT name FROM sqlite_master WHERE TYPE='table' ORDER BY name")
        x = c.fetchall()
        c.close()
        conn.close()
        return x
    
    def insert(self, table_name, captured_jobs):
        conn, c = self.db_switch_on()
        column_query = ('{},' * self.n_columns)[:-1]
        failed = 0
        for each_job in captured_jobs:
            try:
                c.execute("INSERT INTO {} (UID) VALUES ('{}');".format(self.pool_table, each_job['URL']))
                c.execute("INSERT INTO {} ({}) VALUES {};".format(table_name, column_query.format(*each_job), tuple(each_job.values())))
                conn.commit()
            except:
                if 'UNIQUE' in traceback.format_exc():
                    failed += 1
                else:
                    traceback.print_exc()
        print('db: There are {} redundant records\n'.format(failed))
        c.close()
        conn.close()
    
    def fetch(self, table_name):
        conn, c = self.db_switch_on()
        c.execute('SELECT * FROM {};'.format(table_name))
        x = c.fetchall()
        c.close()
        conn.close()
        return x
    
    def clean(self, table_name):
        conn, c = self.db_switch_on()
        c.execute("DELETE FROM {};".format(table_name))
        conn.commit()
        c.close()
        conn.close()
        
    def reset(self): # Use with cautions
        conn, c = self.db_switch_on()
        for each_table in self.allTables():
            if each_table != self.city_table:
                c.execute("DROP TABLE {};".format(each_table[0]))
                conn.commit()
        c.close()
        conn.close()
        
    def poolCheck(self):
        conn, c = self.db_switch_on()
        c.execute("SELECT count(*) FROM {};".format(self.pool_table))
        x = c.fetchall()[0][0]
        c.close()
        conn.close()
        return x
    
    def poolShow(self):
        conn, c = self.db_switch_on()
        c.execute("SELECT * FROM {};".format(self.pool_table))
        x = c.fetchall()
        c.close()
        conn.close()
        return x
    
    def dropEmpty(self):
        conn, c = self.db_switch_on()
        for each_table in self.allTables():
            if each_table not in [self.pool_table, self.city_table]:
                c.execute("SELECT count(*) FROM {};".format(each_table[0]))
                if c.fetchall()[0][0] == 0:
                    c.execute("DROP TABLE {};".format(each_table[0]))
                    conn.commit()
        c.close()
        conn.close()
                                
if __name__ == '__main__':
    test_db = jobDataBase()
