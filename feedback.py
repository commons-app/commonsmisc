#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import cgi
import sys
import json
from wmflabs import db
conn = db.connect('commonswiki')

def jsonify(response):
	return json.dumps(response)

def numofusings(username):
	with conn.cursor() as cur:
		sql = 'select count(*) from globalimagelinks where gil_to in (select log_title from logging_userindex where log_type="upload" and log_user=(select user_id from user where user_name="%s"));' % username
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def numused(username):
	with conn.cursor() as cur:
		sql = 'select count(distinct gil_to) from globalimagelinks where gil_to in (select log_title from logging_userindex where log_type="upload" and log_user=(select user_id from user where user_name="%s"));' % username
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def numfeatured(username):
	awards = ['Featured_pictures_on_Wikimedia_Commons', 'Quality_images']
	sqlins = []
	for award in awards:
		sqlins.append('"' + award + '"')
	sqlin = ", ".join(sqlins)
	with conn.cursor() as cur:
		sql = 'select count(cl_from), cl_to from categorylinks where cl_to in (%s) and cl_type="file" and cl_from in (select log_page from logging_userindex where log_type="upload" and log_user=(select user_id from user where user_name="%s")) group by cl_to;' % (sqlin, username)
		cur.execute(sql)
		data = cur.fetchall()
	response = {}
	for row in data:
		response[row[1]] = row[0]
	for award in awards:
		if award not in response:
			response[award] = 0
	return response

def numthanks(username):
	with conn.cursor() as cur:
		sql = 'select count(*) from logging_logindex where log_type="thanks" and log_title="%s";' % username.replace(' ', '_')
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def numeditedelse(username):
	with conn.cursor() as cur:
		sql = 'select count(*) from revision where rev_page in (select log_page from logging_userindex where log_type="upload" and log_user=(select user_id from user where user_name="%s")) and rev_user!=(select user_id from user where user_name="%s") group by rev_page having count(*)>1' % (username, username)
		cur.execute(sql)
		data = cur.fetchall()
	return len(data)

#Print header
print 'Content-type: application/json\n'

# Fetch params
if 'QUERY_STRING' in os.environ:
        QS = os.environ['QUERY_STRING']
        qs = cgi.parse_qs(QS)
        try:
                user = qs['user'][0].replace('_', ' ')
        except:
		response = {
			'status': 'error',
			'errorCode': 'mustpassparams'
		}
		print jsonify(response)
                sys.exit(0)
	try:
		fetch = qs['fetch'][0].split('|')
	except:
		fetch = [
			'thanksReceived',
			'featuredImages',
			'articlesUsingImages',
			'uniqueUsedImages',
			'imagesEditedBySomeoneElse',
		]
else:
	response = {
		'status': 'error',
		'errorCode': 'mustpassparams'
	}
	print jsonify(response)
        sys.exit(0)

response = {
	'status': 'ok',
	'user': user,
}
if 'thanksReceived' in fetch:
	response['thanksReceived'] = numthanks(user)
if 'featuredImages' in fetch:
	response['featuredImages'] = numfeatured(user)
if 'articlesUsingImages' in fetch:
	response['articlesUsingImages'] = numofusings(user)
if 'uniqueUsedImages' in fetch:
	response['uniqueUsedImages'] = numused(user)
if 'imagesEditedBySomeoneElse' in fetch:
	response['imagesEditedBySomeoneElse'] = numeditedelse(user)

print jsonify(response)
