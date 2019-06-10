#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pymysql

host = "10.128.121.11"
username = "root"
password = "cds-china"
dbname = "cds_bmscontrol"

db = pymysql.connect(host, username, password, dbname)

cursor = db.cursor()


for hostid in ('3'):
      sql = 'UPDATE host SET state="assignable" WHERE id=%s' %hostid
      try:
	sta = cursor.execute(sql)
	print "%s status: %s" %(sql, sta)
	db.commit()
      except Exception,e:
   	db.rollback()

cursor.close()
db.close()

