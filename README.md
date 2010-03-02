# About cloudviz
This package exposes Amazon CloudWatch as a data source for Google Chart Tools.  With it, you can quickly generate graphs like this:
![RequestCount for ELB](http://mbabineau.github.com/cloudviz/example-elb-requestcount.png)

## Getting started
1. Familiarize yourself with:
   * [Amazon CloudWatch](http://aws.amazon.com/cloudwatch/) ([docs](http://docs.amazonwebservices.com/AmazonCloudWatch/latest/DeveloperGuide/))
   * [Google Visualization API](http://code.google.com/apis/visualization/interactive_charts.html) ([docs](http://code.google.com/apis/visualization/documentation/using_overview.html))
2. Download and install:
   * [boto](http://code.google.com/p/boto/) - a Python interface for Amazon Web Services
   * [gviz_api](http://code.google.com/p/google-visualization-python/) - a Python library for creating Google Visualization API data sources
3. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in config.py
4. Make cloudviz.py web-accessible using your favorite HTTP server

# Using cloudviz
cloudviz expects the following query parameters as a JSON-encoded string passed to a qs parameter.  Default values for each parameter may be set in config.py:

* namespace (str) - CloudWatch namespace (ex: _"AWS/ELB"_)
* metric (str) - CloudWatch metric (ex: _"Latency"_)
* unit (str) - CloudWatch init (ex: _"Seconds"_)
* statistics (list of str) - CloudWatch statistics (ex: _["Average","Maximum"]_)
* dimensions (dict of str) - CloudWatch dimensions (ex: _{"LoadBalancerName": "example-lb"}_)
* end_time (date) - end time for queried interval (ex: _new Date_)
* start_time (date) - start time for queried interval (ex: _start_time.setDate(end_time.getDate)_)
* period (int) - (note: must be 60 or greater) (ex: _120_)
* cloudwatch_queries (list of dict) - encapsulates each CloudWatch query, allowing for multiple queries to be graphed in a single chart.  Minimally, cloudwatch_queries must contain one dict with prefix defined.  Optionally, any of the above parameters may also be defined inside one or more _cloudwatch_queries_
  * prefix (str) - text identifier for data returned by a single CloudWatch query. This is prepended to the chart label of each data series (ex: _"My LB "_)

### Example: Graphing CPU utilization of two instances
Here's a JavaScript snippet for building a URL to pass to cloudviz.  See examples/host-cpu.html for the rest of the code.

    var qa = {  
                "namespace": "AWS/EC2",       // CloudWatch namespace (string
                "metric": "CPUUtilization",   // CloudWatch metric (string)
                "unit": "Percent",            // CloudWatch unit (string)
                "statistics": ["Average","Maximum"],      // CloudWatch statistics (list of strings)
                "period": 600,                // CloudWatch period (int)
                "cloudwatch_queries":         // (list of dictionaries)
                [   
                    {
                        "prefix": "Instance 1 CPU ",   // label prefix for associated data sets (string)
                        "dimensions": { "InstanceId": "i-bd14d3d5"} // CloudWatch dimensions (dictionary)
                    },
                    {
                        "prefix": "Instance 2 CPU "
                        "dimensions": { "InstanceId": "i-c514d3ad"}
                    }
                ]
             };
    
    var qs = JSON.stringify(qa);
    var url = 'http://' + window.location.host + '/cloudviz?qs=' + qs;  // assumes cloudviz.py is called at /data

The resulting URL should look something like this:
     http://localhost:8080/cloudviz?qs={%22namespace%22:%22AWS/EC2%22,%22metric%22:%22CPUUtilization%22,%22unit%22:%22Percent%22,%22statistics%22:[%22Average%22,%22Maximum%22],%22period%22:600,%22cloudwatch_queries%22:[{%22prefix%22:%22Instance%201%20CPU%20%22,%22dimensions%22:{%22InstanceId%22:%22i-bd14d3d5%22}},{%22prefix%22:%22Instance%202%20CPU%20%22,%22dimensions%22:{%22InstanceId%22:%22i-c514d3ad%22}}]}&tqx=reqId%3A0

And the graph, when passed through Google's Visualization API:
![CPUUtilization for two instances](http://mbabineau.github.com/cloudviz/example-hosts-cpu.png)

### More examples
Additional examples can be found in examples/, and are written to act as plug-and-play templates.

# Licensing
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

--------------------------------------------------------
Created by Mike Babineau [mike@bizo.com](mike@bizo.com)<br>
Copyright © 2010 [Bizo](http://bizo.com).  All rights reserved.