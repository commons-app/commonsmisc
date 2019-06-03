#!/usr/bin/env python3

import os
import cgi
import sys
from wmflabs import db
import yaml

#Print header
print('Content-type: text/html\n')

# Fetch params
labs = False
if 'QUERY_STRING' in os.environ:
	QS = os.environ['QUERY_STRING']
	qs = cgi.parse_qs(QS)
	try:
		username = qs['user'][0].replace('_', ' ')
	except:
		print('nouser')
		sys.exit(0)
	if 'labs' in qs:
		labs = True
		import pymysql
		# Load config
		__dir__ = os.path.dirname(__file__)
		config = yaml.safe_load(open(os.path.join(__dir__, 'config.yaml')))
		conn = pymysql.connect(db=qs['labs'][0],
			host=config['DB_HOST'],
			user=config['DB_USER'],
			password=config['DB_PASS'],
			charset="utf8",
		)
	else:
		try:
			conn = db.connect(qs['db'][0])
		except:
			conn = db.connect('commonswiki')
else:
	print('nouser')
	sys.exit(0)

##### PROGRAM ####

cur = conn.cursor()
with cur:
	sql = 'select count(*) from logging_userindex where log_type="upload" and log_user=(select user_id from user where user_name="' + username + '");'
	if labs:
		sql = sql.replace('_userindex', '')
	cur.execute(sql)
	data = cur.fetchall()

result = data[0][0]
print(result)
