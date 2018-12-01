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

def articlesUsingImages(logTitleSqlIn):
	with conn.cursor() as cur:
		sql = 'select count(*) from globalimagelinks where gil_to in (%s);' % logTitleSqlIn
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def uniqueUsedImages(logTitleSqlIn):
	with conn.cursor() as cur:
		sql = 'select count(distinct gil_to) from globalimagelinks where gil_to in (%s);' % logTitleSqlIn
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def imagesEditedBySomeoneElse(userId, logPageSqlIn):
	with conn.cursor() as cur:
		sql = 'select count(*) from revision where rev_page in (%s) and rev_user!=%d group by rev_page having count(*)>1' % (logPageSqlIn, userId)
		cur.execute(sql)
		data = cur.fetchall()
	return len(data)

def deletedUploads(username):
	with conn.cursor() as cur:
		sql = 'select count(*) from filearchive_userindex where fa_user_text="' + username + '";'
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def getUserId(username):
    	with conn.cursor() as cur:
		sql = 'select user_id from user where user_name="%s";' % username
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def getLogTitleAndPage(userId):
	with conn.cursor() as cur:
		sql = 'select log_title, log_page from logging_userindex where log_type="upload" and log_user=%d;' % userId
		cur.execute(sql)
		data = cur.fetchall()
	counter = 0
	logTitlesSqlIns = []
	logPagesSqlIns = []
	for row in data:
		logTitlesSqlIns.append('"' + row[0] + '"')
		logPagesSqlIns.append('"' + row[1] + '"')
		counter = counter + 1

	logTitlesSqlIn = ", ".join(logTitlesSqlIns)
	logPagesSqlIn = ", ".join(logPagesSqlIns)
	return logTitlesSqlIn, logPagesSqlIn

#Print header
print 'Content-type: application/json'

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
		print "Status: 400 Bad Request\n"
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
	print "Status: 400 Bad Request\n"
	print jsonify(response)
        sys.exit(0)

response = {
	'status': 'ok',
	'user': user,
}

userid = getUserId(user)
if 'articlesUsingImages' in fetch or 'uniqueUsedImages' in fetch or 'imagesEditedBySomeoneElse' in fetch:
	logTitleSqlIn, logPageSqlIn = getLogTitleAndPage(userid)

if 'thanksReceived' in fetch:
	response['thanksReceived'] = thanksReceived(user)
if 'featuredImages' in fetch:
	response['featuredImages'] = featuredImages(userid)
if 'articlesUsingImages' in fetch:
	response['articlesUsingImages'] = articlesUsingImages(logTitleSqlIn)
if 'uniqueUsedImages' in fetch:
	response['uniqueUsedImages'] = uniqueUsedImages(logTitleSqlIn)
if 'imagesEditedBySomeoneElse' in fetch:
	response['imagesEditedBySomeoneElse'] = imagesEditedBySomeoneElse(userid, logPageSqlIn)
if 'deletedUploads' in fetch:
	response['deletedUploads'] = deletedUploads(user)

print
print jsonify(response)
