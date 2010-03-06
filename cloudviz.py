#!/usr/bin/python
"""
cloudviz.py
This script exposes Amazon EC2 CloudWatch as a data source for the Google Visualization API

Requirements:
- AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY, read in from config.py
- boto, a Python interface for Amazon Web Services (http://code.google.com/p/boto/)
- gviz_api, a Python library for creating Google Visualization API data sources 
  (http://code.google.com/p/google-visualization-python/)

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

from sys import exit #for debugging
from cgi import FieldStorage
from datetime import datetime
from operator import itemgetter
import gviz_api
from boto import connect_cloudwatch
from boto.ec2.cloudwatch.metric import Metric
from django.utils import simplejson
from config import *

def main():
    # Create connection with "is_secure=false"" for App Engine compatability
    c = connect_cloudwatch(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, is_secure=False)

    # Initialize data description, columns to be returned, and result set
    description = { "Timestamp": ("datetime", "Timestamp")}
    columns = ["Timestamp"]
    rs = []
    
    # Parse the query string
    qs = FieldStorage()
    qa = simplejson.loads(qs.getvalue('qs'))

    # Build option list
    opts = ['unit','metric','namespace','statistics','period', 'dimensions', 'prefix', 'start_time', 'end_time', 'calc_rate']
    
    # Set defaults
    args = DEFAULTS

    # Set passed args
    for opt in opts:
        if opt in qa: args[opt] = qa[opt]

    # Convert timestamps to datetimes if necessary
    for time in ['start_time','end_time']:
        if type(args[time]) == str or type(args[time]) == unicode: 
            args[time] = datetime.strptime(args[time].split(".")[0], '%Y-%m-%dT%H:%M:%S')
        
    # Parse, build, and run each CloudWatch query
    cw_queries = qa['cloudwatch_queries']
    cw_opts = ['unit','metric','namespace','statistics','period','dimensions','prefix', 'calc_rate']
    for cw_q in cw_queries:
        # Override lower-level vars
        for opt in cw_opts:
            if opt in cw_q: args[opt] = cw_q[opt]
            
        # Pull data from EC2
        results = c.get_metric_statistics(  args['period'], args['start_time'], args['end_time'], 
                                            args['metric'], args['namespace'], args['statistics'],
                                            args['dimensions'], args['unit'])
        # Format/transform results
        for d in results:
            # Convert timestamps to datetime objects
            d.update({u'Timestamp': datetime.strptime(d[u'Timestamp'],"%Y-%m-%dT%H:%M:%SZ")})
            # If desired, calculate rate as per-second values
            if args['calc_rate'] == True and 'Sum' in args['statistics']: d.update({u'Sum': d[u'Sum']/args['period']})
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
            description[args['prefix']+stat] = ('number', args['prefix']+stat)
            columns.append(args['prefix']+stat)       
    
    # Sort data and present    
    data = sorted(rs, key=itemgetter(u'Timestamp'))
    data_table = gviz_api.DataTable(description)
    data_table.LoadData(data)

    print "Content-type: text/plain"
    print
    print data_table.ToJSonResponse(columns_order=columns, order_by="Timestamp")

if __name__ == "__main__":
    main()