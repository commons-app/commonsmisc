#!/usr/bin/env python

import os
import cgi
import sys
from wmflabs import db

#Print header
print 'Content-type: text/html\n'

# Fetch params
if 'QUERY_STRING' in os.environ:
	QS = os.environ['QUERY_STRING']
	qs = cgi.parse_qs(QS)
	try:
		username = qs['user'][0]
	except:
		print 'nouser'
		sys.exit(0)
else:
	print 'nouser'
	sys.exut(0)

##### PROGRAM ####

conn = db.connect('commonswiki')
cur = conn.cursor()
with cur:
	sql = 'select count(*) from logging_userindex where log_type="upload" and log_user=(select user_id from user where user_name="' + username + '");'
	cur.execute(sql)
	data = cur.fetchall()

result = data[0][0]
print result
