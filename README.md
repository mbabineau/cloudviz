# About cloudviz
This package exposes Amazon CloudWatch as a data source for Google Chart Tools.  With it, you can quickly generate graphs like this:
![RequestCount for ELB](http://mbabineau.github.com/cloudviz/example-elb-requestcount.png)

Cloudviz is proudly sponsored by [Bizo](http://bizo.com).  For details on the cloudviz's origin, see this [blog post](http://dev.bizo.com/2010/03/introducing-cloudviz.html).

If you're looking for easiest way to start graphing CloudWatch data, check out [Cloudgrapher](http://www.cloudgrapher.com).  Cloudgrapher is a free CloudWatch dashboard, and is effectively a hosted, batteries-included extension of cloudviz.

## Getting started
1. Familiarize yourself with:
   * [Amazon CloudWatch](http://aws.amazon.com/cloudwatch/) ([docs](http://docs.amazonwebservices.com/AmazonCloudWatch/latest/DeveloperGuide/))
   * [Google Visualization API](https://developers.google.com/chart/) ([docs](https://developers.google.com/chart/interactive/docs/))
2. Download and install:
   * [boto](https://github.com/boto/boto) - a Python interface for Amazon Web Services
   * [gviz_api](https://github.com/google/google-visualization-python) - a Python library for creating Google Visualization API data sources
   * [pytz](https://pypi.python.org/pypi/pytz/) - world timezone definitions
3. Set **AWS_ACCESS_KEY_ID **and **AWS_SECRET_ACCESS_KEY **in <code>settings.py</code>
4. Make <code>cloudviz.py</code> web-accessible using your favorite HTTP server

# Using cloudviz
cloudviz expects the following query parameters as a JSON-encoded string passed to a qs parameter.  Default values for each parameter may be set in <code>settings.py</code>:

* `namespace` (str) - CloudWatch namespace (e.g., _"AWS/ELB"_)
* `metric` (str) - CloudWatch metric (e.g., _"Latency"_)
* `unit` (str) - CloudWatch unit (e.g., _"Seconds"_)
* `statistics` (list of str) - CloudWatch statistics (e.g., _["Average","Maximum"]_)
* `dimensions` (dict of str) - CloudWatch dimensions (e.g., _{"LoadBalancerName": "example-lb"}_)
* `end_time` (date) - end time for queried interval (e.g., _new Date_)
* `start_time` (date) - start time for queried interval (e.g., _start_time.setDate(end_time.getDate-3)_)
* `range` (int) - desired time range, in hours, for queried interval (e.g., _24_).  Note: `range` may be substituted for `start_time`, `end_time`, or both:
  * if `range` and `end_time` are specified, `start_time` is calculated as ( `end_time` - `range` )
  * if `range` and `start_time` are specified, `end_time` is calculated as ( `start_time` + `range` )
  * if only `range` is specified, `end_time` is set to the current time and `start_time` is calculated as ( current time - `range` )  
* `period` (int) - (optional) CloudWatch period (e.g., _120_).  Notes: must be a multiple of 60; if `period` is not specified, it will be automatically calculated as the smallest valid value (resulting in the most data points being returned) for the queried interval.
* `region` (str) - (optional) AWS region (e.g., _"us-west-1"_; default is "us-east-1")
* `calc_rate` (bool) - (optional) when set to _True_ and `statistics` includes _"Sum"_, cloudviz converts _Sum_ values to per-second _Rate_ values by dividing _Sum_ by seconds in `period` (e.g., for _RequestCount_, 150 Requests per period / 60 seconds per period = 2.5 Requests per second)
* `cloudwatch_queries` (list of dict) - encapsulates each CloudWatch query, allowing for multiple queries to be graphed in a single chart.  Minimally, `cloudwatch_queries` must contain one dict with prefix defined.  Optionally, any of the above parameters may also be defined inside one or more `cloudwatch_queries`
  * `prefix` (str) - text identifier for data returned by a single CloudWatch query. This is prepended to the chart label of each data series (e.g., _"My LB "_)

### Example: Graphing CPU utilization of two instances
Here's a JavaScript snippet for building a URL to pass to cloudviz.  See examples/host-cpu.html for the rest of the code.  Note that **start_time **and **end_time **are set in <code>settings.py</code>. 

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
Additional examples can be found in <code>examples/</code>, and are written to act as plug-and-play templates.

# Licensing
Copyright 2010 [Bizo, Inc.](http://bizo.com) (Mike Babineau <[michael.babineau@gmail.com](mailto:michael.babineau@gmail.com)>)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
