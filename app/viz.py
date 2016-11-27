from __future__ import division

from flask import render_template, redirect, flash, request, jsonify, url_for, Response
from app import app

import json
import psycopg2


@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/viz')
def viz():
    return render_template('viz.html')


def to_csv(d, fields):
    d.insert(0, fields)
    return Response('\n'.join([",".join(e) for e in d]), mimetype='text/csv')


@app.route('/sentiment_agg')
def sentiment_agg():
    db = psycopg2.connect(host='ec2-54-208-219-223.compute-1.amazonaws.com',
                          database='election',
                          user='elections',
                          password='election2016')
    curs = db.cursor()
    curs.execute("""select person, a.website, to_timestamp(timestamp)::date::varchar, avg(sentiment)::varchar, count(*)::varchar 
                    from data a join top_websites b on a.website = b.website
                    where person in ('Trump','Clinton') group by 1, 2, 3;
                """)
    d = curs.fetchall()
    fields = ('Candidate', 'Source', 'Date', 'Score', 'Count')
    return to_csv(d, fields)
