#!/usr/bin/python

"""
cloudviz.py
This script exposes Amazon EC2 CloudWatch as a data source for the Google Visualization API

Requirements:
- AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY, read in from settings.py
- boto, a Python interface for Amazon Web Services (http://code.google.com/p/boto/)
- gviz_api, a Python library for creating Google Visualization API data sources 
  (http://code.google.com/p/google-visualization-python/)

Cloudviz project maintained here: http://github.com/mbabineau/cloudviz
--------
Copyright 2010 Bizo, Inc. (Mike Babineau <mike@bizo.com>)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import cgi
import operator
from datetime import datetime, timedelta
from django.utils import simplejson

# Google Visualization API
import gviz_api

from boto import connect_cloudwatch
from boto.ec2.cloudwatch.metric import Metric

from settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DEFAULTS, CW_MAX_DATA_POINTS, CW_MIN_PERIOD

def get_cloudwatch_data(cloudviz_query, request_id, aws_access_key_id=None, aws_secret_access_key=None):
    """
    Query CloudWatch and return the results in a Google Visualizations API-friendly format

    Arguments:
    `cloudviz_query` -- (dict) parameters and values to be passed to CloudWatch (see README for more information)
    `request_id` -- (int) Google Visualizations request ID passed as part of the "tqx" parameter
    """
    # Initialize data description, columns to be returned, and result set
    description = { "Timestamp": ("datetime", "Timestamp")}
    columns = ["Timestamp"]
    rs = []

    # Build option list
    opts = ['unit','metric','namespace','statistics','period', 'dimensions', 'prefix', 
            'start_time', 'end_time', 'calc_rate', 'region', 'range']
    
    # Set default parameter values from config.py
    qa = DEFAULTS.copy()
    
    # Set passed args
    for opt in opts:
        if opt in cloudviz_query: qa[opt] = cloudviz_query[opt]
    
    # Convert timestamps to datetimes if necessary
    for time in ['start_time','end_time']:
        if time in qa:
            if type(qa[time]) == str or type(qa[time]) == unicode: 
                qa[time] = datetime.strptime(qa[time].split(".")[0], '%Y-%m-%dT%H:%M:%S')

    # If both start_time and end_time are specified, do nothing.  
    if 'start_time' in qa and 'end_time' in qa:
        pass
    # If only one of the times is specified, fill in the other based on range
    elif 'start_time' in qa and 'range' in qa:
        qa['end_time'] = qa['start_time'] + timedelta(hours=qa['range'])
    elif 'range' in qa and 'end_time' in qa:
        qa['start_time'] = qa['end_time'] - timedelta(hours=qa['range'])
    # If neither is specified, use range leading up to current time
    else:
        qa['end_time'] = datetime.now()
        qa['start_time'] = qa['end_time'] - timedelta(hours=qa['range'])
    
    # Parse, build, and run each CloudWatch query
    cloudwatch_opts = ['unit', 'metric', 'namespace', 'statistics', 'period', 'dimensions', 'prefix', 'calc_rate', 'region']
    for cloudwatch_query in cloudviz_query['cloudwatch_queries']:
        args = qa.copy()
        # Override top-level vars
        for opt in cloudwatch_opts:
            if opt in cloudwatch_query: args[opt] = cloudwatch_query[opt]
        
        # Calculate time range for period determination/sanity-check
        delta = args['end_time'] - args['start_time']
        delta_seconds = ( delta.days * 24 * 60 * 60 ) + delta.seconds + 1 #round microseconds up

        # Determine min period as the smallest multiple of 60 that won't result in too many data points
        min_period = 60 * int(delta_seconds / CW_MAX_DATA_POINTS / 60)
        if ((delta_seconds / CW_MAX_DATA_POINTS) % 60) > 0:
            min_period += 60
        
        if 'period' in qa:
            if args['period'] < min_period:
                args['period'] = min_period
        else:
            args['period'] = min_period
        
        # Make sure period isn't smaller than CloudWatch allows
        if args['period'] < CW_MIN_PERIOD: 
            args['period'] = CW_MIN_PERIOD
        
        # Convert a region argument to an AWS CloudWatch endpoint, defaulting to us-east-1
        if not 'region' in args: 
            endpoint = 'us-east-1.monitoring.amazonaws.com'
        else: 
            endpoint = '%s.monitoring.amazonaws.com' % args['region']
        
        # Use AWS keys if provided, otherwise just let the boto look it up
        if aws_access_key_id and aws_secret_access_key:
            c = connect_cloudwatch(aws_access_key_id, aws_secret_access_key, is_secure=False)
        else:
            c = connect_cloudwatch(is_secure=False)
        
        # Pull data from EC2
        results = c.get_metric_statistics(  args['period'], args['start_time'], args['end_time'], 
                                            args['metric'], args['namespace'], args['statistics'],
                                            args['dimensions'], args['unit'])
        # Format/transform results
        for d in results:
            # Convert timestamps to datetime objects
            d.update({u'Timestamp': datetime.strptime(d[u'Timestamp'],"%Y-%m-%dT%H:%M:%SZ")})
            # If desired, convert Sum to a per-second Rate
            if args['calc_rate'] == True and 'Sum' in args['statistics']: d.update({u'Rate': d[u'Sum']/args['period']})
            # Change key names
            keys = d.keys()
            keys.remove('Timestamp')
            for k in keys:
                new_k = args['prefix']+k
                d[new_k] = d[k]
                del d[k]
    
        rs.extend(results)
        
        # Build data description and columns to be return
        description[args['prefix']+'Samples'] = ('number', args['prefix']+'Samples')
        description[args['prefix']+'Unit'] = ('string', args['unit']) 
        for stat in args['statistics']:
            # If Rate is desired, update label accordingly
            if stat == 'Sum' and args['calc_rate'] == True:
                stat = 'Rate'
            description[args['prefix']+stat] = ('number', args['prefix']+stat)
            columns.append(args['prefix']+stat)       
    
    # Sort data and present    
    data = sorted(rs, key=operator.itemgetter(u'Timestamp'))
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    results = data_table.ToJSonResponse(columns_order=columns, order_by="Timestamp", req_id=request_id)
    return results

def main():
    # Parse the query string
    fs = cgi.FieldStorage()
    cloudviz_query = simplejson.loads(fs.getvalue('qs'))
    
    # Convert tqx to dict; tqx is a set of colon-delimited key/value pairs separated by semicolons
    tqx = {}
    for s in fs.getvalue('tqx').split(';'):
        key = s.split(':')[0]
        value = s.split(':')[1]
        tqx.update({key:value})
    
    # Set reqId so we know who to send data back to
    request_id = tqx['reqId']
        
    results = get_cloudwatch_data(cloudviz_query, request_id, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    print "Content-type: text/plain"
    print
    print results

if __name__ == "__main__":
    status = main()
    sys.exit(status)
