from __future__ import division

from flask import render_template, request, Response, jsonify
from app import app

import json
import psycopg2
import psycopg2.extras


@app.route('/index')
def index():
    return render_template('home.html')


@app.route('/viz')
def viz():
    return render_template('viz.html')


def to_csv(d, fields):
    d.insert(0, fields)
    return Response('\n'.join([",".join(map(str, e)) for e in d]), mimetype='text/csv')


@app.route('/hist_data', methods=['GET', 'POST'])
def hist_data():
    website = request.args.get('website')
    person = request.args.get('person')
    db = psycopg2.connect(host='ec2-54-208-219-223.compute-1.amazonaws.com',
                          database='election',
                          user='elections',
                          password='election2016')
    curs = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if website:
        sql = """select a.bin, sum(coalesce(count,0)) from histogram_bins a
                left join (select * from data_binned where website = '%s' and person = '%s') b on a.bin = b.bin
                group by 1 order by 1""" % (website, person)
    else:
        sql = """select a.bin, sum(coalesce(count,0)) from histogram_bins a
                left join (select * from data_binned where person = '%s') b on a.bin = b.bin
                group by 1 order by 1""" % person
    print(sql)
    curs.execute(sql)
    d = curs.fetchall()
    fields = ('bin', 'sum')
    return jsonify(data=d)
