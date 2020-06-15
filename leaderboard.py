#!/usr/bin/env python3

import os
import cgi
import sys
from wmflabs import db
import json
import yaml
from datetime import datetime, timedelta
import pymysql


def jsonify(response):
    return json.dumps(response)


# Print header
print('Content-type: application/json\n')

# Fetch params
labs = False
if 'QUERY_STRING' in os.environ:
    QS = os.environ['QUERY_STRING']
    qs = cgi.parse_qs(QS)
    try:
        duration = qs['duration'][0]
        username = qs['user'][0].replace('_', ' ')
    except:
        print(jsonify({'status': '400'}))
        sys.exit(0)
    if 'labs' in qs:
        labs = True
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
    print(jsonify({'status': '500'}))
    sys.exit(0)

##### PROGRAM ####


def get_res(status, user, uploads):
    response = {'status': status, 'user': user,  'uploads': uploads}
    return response


def get_sql(duration, username):
    if duration == 'all':
        return """select count(*)
        from logging_userindex
        where log_type="upload"
        and
        log_actor=(select actor_id from actor where actor_name="{username}");""".format(username=username)

    elif duration == 'year':
        start_time = str(datetime.today().replace(
            month=1, day=1).strftime("%Y%m%d"))+"000000"
        end_time = str(datetime.today().strftime("%Y%m%d%H%M%S"))
        return """select count(*)
        from logging_userindex
        where log_type="upload"
        and
        log_actor=(select actor_id from actor where actor_name="{username}")
        and
        log_timestamp > "{start_time}" and log_timestamp < "{end_time}";""".format(username=username, start_time=start_time, end_time=end_time)

    elif duration == 'weekly':
        today = datetime.now().date()
        start_time = str(
            (today - timedelta(days=today.weekday())).strftime("%Y%m%d%H%M%S"))
        end_time = str(datetime.today().strftime("%Y%m%d%H%M%S"))
        return """select count(*)
        from logging_userindex
        where log_type="upload"
        and
        log_actor=(select actor_id from actor where actor_name="{username}")
        and
        log_timestamp > "{start_time}" and log_timestamp < "{end_time}";""".format(username=username, start_time=start_time, end_time=end_time)
    
    else:
        print(jsonify({'status': '400'}))
        sys.exit(0)


cur = conn.cursor()
with cur:
    sql = get_sql(duration, username)
    if labs:
        sql = sql.replace('_userindex', '')
    cur.execute(sql)
    data = cur.fetchall()

result = data[0][0]
print(jsonify(get_res('200', username, result)))
