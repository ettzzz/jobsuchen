#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 10:22:02 2019

@author: eriti
"""


import sqlite3
import traceback
import time

class jobDataBase():
    
    def __init__(self, user_id = '000'):
        self.database = 'jobs.db'
        self.pool_table = 'pool' + user_id
        self.city_table = 'cityset'
        self.job_table = 'jobs' + user_id
        self.buildPool()
        self.buildCityset()
        self.buildJobtable()
        self.buildStampdrawer()
        
    def db_switch_on(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        return conn, c
    
    def db_switch_off(self, conn, c):
        c.close()
        conn.close()
    
    def buildPool(self):
        tables = self.allTables()
        conn, c = self.db_switch_on()
        if (self.pool_table,) not in tables:
            c.execute("CREATE TABLE {}(UID TEXT PRIMARY KEY NOT NULL);".format(self.pool_table))
            conn.commit()
        self.db_switch_off(conn, c)
        
    def buildCityset(self):
        tables = self.allTables()
        conn, c = self.db_switch_on()
        if (self.city_table,) not in tables:
            c.execute("CREATE TABLE {}(\
                      UID INTEGER PRIMARY KEY AUTOINCREMENT,\
                      pinyin TEXT NOT NULL,\
                      linkedin TEXT,\
                      indeed TEXT,\
                      zhilian TEXT,\
                      liepin TEXT,\
                      lagou TEXT,\
                      bosszhipin TEXT,\
                      yingjiesheng TEXT,\
                      dajie TEXT);".format(self.city_table))
            conn.commit()
        self.db_switch_off(conn, c)
        
    def insertCityset(self, city_pinyin, web, city_code):
        conn, c = self.db_switch_on()
        c.execute("SELECT pinyin FROM {};".format(self.city_table))
        cities = c.fetchall()
        if (city_pinyin,) not in cities:
            value = "('{}', '{}')".format(city_pinyin, city_code)
            c.execute("INSERT INTO {} (pinyin, {}) VALUES {};".format(self.city_table, web, value))
        else:
            c.execute("UPDATE {} SET {} = '{}' WHERE pinyin = '{}';".format(self.city_table, web, city_code, city_pinyin))
        conn.commit()
        self.db_switch_off(conn, c)
        
    def getCityCode(self, city_pinyin, web):
        conn, c = self.db_switch_on()
        c.execute("SELECT {} FROM {} WHERE pinyin = \'{}\';".format(web, self.city_table, city_pinyin))
        x = c.fetchall()
        self.db_switch_off(conn, c)
        return x[0][0]
        
    def buildJobtable(self):
        tables = self.allTables()
        conn, c = self.db_switch_on()
        if (self.job_table,) not in tables:
            c.execute("CREATE TABLE {}(\
                            UID TEXT PRIMARY KEY NOT NULL,\
                            Source CHAR(20) NOT NULL,\
                            Position TEXT NOT NULL,\
                            Release CHAR(20) NOT NULL,\
                            Company TEXT NOT NULL,\
                            Location TEXT,\
                            Payment CHAR(20),\
                            URL TEXT NOT NULL,\
                            Keyword TEXT NOT NULL,\
                            Timestamp INTEGER NOT NULL\
                            );".format(self.job_table))
        conn.commit()
        self.db_switch_off(conn, c)
    
    def buildStampdrawer(self):
        tables = self.allTables()
        if ('timestamp',) not in tables:
            conn, c = self.db_switch_on()
            c.execute("CREATE TABLE timestamp(\
                      UID INTEGER PRIMARY KEY AUTOINCREMENT,\
                      laststamp INTEGER NOT NULL);")
            conn.commit()
            self.db_switch_off(conn, c)
            self.addTimestamp(1900000000)
        
    def readTimestamp(self):
        conn, c = self.db_switch_on()
        c.execute("SELECT laststamp FROM timestamp;")
        x = c.fetchall()
        self.db_switch_off(conn, c)
        return x[-1][0]
    
    def addTimestamp(self, ts):
        conn, c = self.db_switch_on()
        c.execute("INSERT INTO timestamp (laststamp) VALUES ({});".format(ts))
        conn.commit()
        self.db_switch_off(conn, c)
        
    def allTables(self):
        conn, c = self.db_switch_on()
        c.execute("SELECT name FROM sqlite_master WHERE TYPE='table' ORDER BY name")
        x = c.fetchall()
        self.db_switch_off(conn, c)
        return x
    
    def insert(self, captured_jobs):
        conn, c = self.db_switch_on()
        timestamp = int(time.strftime('%y%m%d%H%M',time.localtime(time.time())))
        for i, each_job in enumerate(captured_jobs):
            try:
                c.execute("INSERT INTO {} (UID) VALUES ('{}');".format(self.pool_table, each_job['UID']))
                values = (each_job['UID'], each_job['Source'], each_job['Position'], each_job['Release'], each_job['Company'],\
                          each_job['Location'], each_job['Payment'], each_job['URL'], each_job['Keyword'], timestamp)
                c.execute("INSERT INTO {} (UID, Source, Position, Release, Company, Location, Payment, URL, Keyword,Timestamp) \
                          VALUES {};".format(self.job_table, values))
            except:
                traceback.print_exc()
            conn.commit()
        self.db_switch_off(conn, c)
    
    def fetch(self):
        conn, c = self.db_switch_on()
        c.execute("SELECT * FROM {};".format(self.job_table))
        x = c.fetchall()
        self.db_switch_off(conn, c)
        return x

    def fetchnew(self):
        ts = self.readTimestamp()
        conn, c = self.db_switch_on()
        c.execute("SELECT * FROM {} WHERE Timestamp > {};".format(self.job_table, ts))
        x = c.fetchall()
        self.db_switch_off(conn, c)
        return x
    
    def clean(self):
        conn, c = self.db_switch_on()
        c.execute("DELETE FROM {};".format(self.job_table))
        conn.commit()
        self.db_switch_off(conn, c)
        
    def reset(self): # Use with cautions
        conn, c = self.db_switch_on()
        for each_table in self.allTables():
            try:
                if each_table != self.city_table:
                    c.execute("DROP TABLE {};".format(each_table[0]))
                    conn.commit()
            except:
                continue
        self.db_switch_off(conn, c)
        
    def poolCheck(self):
        conn, c = self.db_switch_on()
        c.execute("SELECT count(*) FROM {};".format(self.pool_table))
        x = c.fetchall()[0][0]
        self.db_switch_off(conn, c)
        return x
    
    def poolShow(self):
        conn, c = self.db_switch_on()
        c.execute("SELECT * FROM {};".format(self.pool_table))
        x = c.fetchall()
        self.db_switch_off(conn, c)
        return x
    
                                
if __name__ == '__main__':
    test_db = jobDataBase()

                
        
