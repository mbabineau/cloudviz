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
3. Copy/move <code>config.py.template</code> to <code>config.py</code>
4. Set **AWS_ACCESS_KEY_ID **and **AWS_SECRET_ACCESS_KEY **in <code>config.py</code>
5. Make <code>cloudviz.py</code> web-accessible using your favorite HTTP server

# Using cloudviz
cloudviz expects the following query parameters as a JSON-encoded string passed to a qs parameter.  Default values for each parameter may be set in <code>config.py</code>:

* __namespace __(str) - CloudWatch namespace (e.g., _"AWS/ELB"_)
* __metric __(str) - CloudWatch metric (e.g., _"Latency"_)
* __unit __(str) - CloudWatch unit (e.g., _"Seconds"_)
* __statistics __(list of str) - CloudWatch statistics (e.g., _["Average","Maximum"]_)
* __dimensions __(dict of str) - CloudWatch dimensions (e.g., _{"LoadBalancerName": "example-lb"}_)
* __end_time __(date) - end time for queried interval (e.g., _new Date_)
* __start_time __(date) - start time for queried interval (e.g., _start_time.setDate(end_time.getDate-3)_)
* __period __(int) - (note: must be 60 or greater) (e.g., _120_)
* __calc_rate __(bool) - (optional) when set to _True_ and **statistics** includes _"Sum"_, cloudviz converts _Sum_ values to per-second _Rate_ values by dividing _Sum_ by seconds in _period_ (e.g., for _RequestCount_, 150 Requests per period / 60 seconds per period = 2.5 Requests per second)
* __cloudwatch_queries __(list of dict) - encapsulates each CloudWatch query, allowing for multiple queries to be graphed in a single chart.  Minimally, **cloudwatch_queries **must contain one dict with prefix defined.  Optionally, any of the above parameters may also be defined inside one or more **cloudwatch_queries **
  * __prefix __(str) - text identifier for data returned by a single CloudWatch query. This is prepended to the chart label of each data series (e.g., _"My LB "_)

### Example: Graphing CPU utilization of two instances
Here's a JavaScript snippet for building a URL to pass to cloudviz.  See examples/host-cpu.html for the rest of the code.  Note that **start_time **and **end_time **are set in <code>config.py</code>. 

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
Copyright 2010 [Bizo, Inc.](http://bizo.com) (Mike Babineau <[mike@bizo.com](mailto:mike@bizo.com)>)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.