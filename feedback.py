#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import cgi
import sys
import json
import yaml
from wmflabs import db

def jsonify(response):
	return json.dumps(response)

def clearSql(sql):
	if labs:
		return sql.replace('_logindex', '').replace('_userindex', '')
	else:
		return sql

def thanksReceived(username):
	with conn.cursor() as cur:
		sql = 'select count(*) from logging_logindex where log_type="thanks" and log_title="%s";' % username.replace(' ', '_')
		sql = clearSql(sql)
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
		sql = clearSql(sql)
		cur.execute(sql)
		data = cur.fetchall()
	response = {}
	for row in data:
		response[row[1].decode('utf-8')] = row[0]
	for award in awards:
		if award not in response:
			response[award] = 0
	return response

def articlesUsingImages(userId):
	with conn.cursor() as cur:
		sql = 'select count(*) from globalimagelinks where gil_to in (select log_title from logging_userindex where log_type="upload" and log_user=%d);' % userId
		sql = clearSql(sql)
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def uniqueUsedImages(userId):
	with conn.cursor() as cur:
		sql = 'select count(distinct gil_to) from globalimagelinks where gil_to in (select log_title from logging_userindex where log_type="upload" and log_user=%d);' % userId
		sql = clearSql(sql)
		cur.execute(sql)
		data = cur.fetchall()
	return data[0][0]

def imagesEditedBySomeoneElse(userId):
	with conn.cursor() as cur:
		sql = 'select count(*) from revision where rev_page in (select log_page from logging_userindex where log_type="upload" and log_user=%d) and rev_user!=%d group by rev_page having count(*)>1' % (userId, userId)
		sql = clearSql(sql)
		cur.execute(sql)
		data = cur.fetchall()
	return len(data)

def deletedUploads(username):
	with conn.cursor() as cur:
		sql = 'select count(*) from filearchive_userindex where fa_user_text="' + username + '";'
		sql = clearSql(sql)
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
print('Content-type: application/json')

# Fetch params
labs = False
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
		print("Status: 400 Bad Request\n")
		print(jsonify(response))
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
		except KeyError:
			conn = db.connect('commonswiki')
else:
	response = {
		'status': 'error',
		'errorCode': 'mustpassparams'
	}
	print("Status: 400 Bad Request\n")
	print(jsonify(response))
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

print()
print(jsonify(response))
