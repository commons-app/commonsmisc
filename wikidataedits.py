#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import cgi
import json
import sys
from wmflabs import db

def jsonify(response):
	return json.dumps(response)

#Print header
print 'Content-type: application/json'

# Fetch params
if 'QUERY_STRING' in os.environ:
	QS = os.environ['QUERY_STRING']
	qs = cgi.parse_qs(QS)
	try:
		username = qs['user'][0].replace('_', ' ')
	except:
		print 'nouser'
		sys.exit(0)
else:
	print 'nouser'
	sys.exit(0)

##### PROGRAM ####

conn = db.connect('wikidatawiki')
cur = conn.cursor()
with cur:
	sql = 'select count(*) as edit_count from change_tag join revision on rev_id=ct_rev_id where ct_tag="wikimedia-commons-app" and rev_user_text="' + username + '";'
	cur.execute(sql)
	data = cur.fetchall()

result = data[0][0]

response = {
    'edits': result
}

print
print jsonify(response)