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

def thanksReceived(username):
	with conn.cursor() as cur:
		sql = 'select count(*) from logging_logindex where log_type="thanks" and log_title="%s";' % username.replace(' ', '_')
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def featuredImages(userId):
	awards = ['Featured_pictures_on_Wikimedia_Commons', 'Quality_images']
	sqlins = []
	for award in awards:
		sqlins.append('"' + award + '"')
	sqlin = ", ".join(sqlins)
	with conn.cursor() as cur:
		sql = 'select count(cl_from), cl_to from categorylinks where cl_to in (%s) and cl_type="file" and cl_from in (select log_page from logging_userindex where log_type="upload" and log_user=%d) group by cl_to;' % (sqlin, userId)
		cur.execute(sql)
		data = cur.fetchall()
	response = {}
	for row in data:
		response[row[1]] = row[0]
	for award in awards:
		if award not in response:
			response[award] = 0
	return response

def articlesUsingImages(userId):
	with conn.cursor() as cur:
		sql = 'select count(*) from globalimagelinks where gil_to in (select log_title from logging_userindex where log_type="upload" and log_user=%d);' % userId
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def uniqueUsedImages(userId):
	with conn.cursor() as cur:
		sql = 'select count(distinct gil_to) from globalimagelinks where gil_to in (select log_title from logging_userindex where log_type="upload" and log_user=%d);' % userId
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def imagesEditedBySomeoneElse(userId):
	with conn.cursor() as cur:
		sql = 'select count(*) from revision where rev_page in (select log_page from logging_userindex where log_type="upload" and log_user=%d) and rev_user!=%d group by rev_page having count(*)>1' % (userId, userId)
		cur.execute(sql)
		data = cur.fetchall()
	return len(data)

def deletedUploads(username):
	with conn.cursor() as cur:
		sql = 'select count(*) from filearchive where fa_user_text="' + username + '";'
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def getUserId(username):
    	with conn.cursor() as cur:
		sql = 'select user_id from user where user_name="%s";' % username
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

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
			'deletedUploads',
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

userid = getUserId(user)

if 'thanksReceived' in fetch:
	response['thanksReceived'] = thanksReceived(user)
if 'featuredImages' in fetch:
	response['featuredImages'] = featuredImages(userid)
if 'articlesUsingImages' in fetch:
	response['articlesUsingImages'] = articlesUsingImages(userid)
if 'uniqueUsedImages' in fetch:
	response['uniqueUsedImages'] = uniqueUsedImages(userid)
if 'imagesEditedBySomeoneElse' in fetch:
	response['imagesEditedBySomeoneElse'] = imagesEditedBySomeoneElse(userid)
if 'deletedUploads' in fetch:
	response['deletedUploads'] = deletedUploads(user)

print jsonify(response)
