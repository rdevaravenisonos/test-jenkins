#!/usr/bin/env python2.7

import base64
import os
import re
import ssl
import urllib2


UPSTREAM_JOB_NAME = os.getenv('JOB_NAME')
UPSTREAM_BUILD_ID = os.getenv('BUILD_NUMBER')
JENKINS_URL = 'http://10.25.12.43:8080'
JENKINS_USER = 'admin'
JENKINS_PASSWORD = 'BocceBal1'

ENCODED_TOKEN = base64.encodestring('%s:%s' % (JENKINS_USER, JENKINS_PASSWORD)).replace('\n', '')
HEADERS = {
    'Authorization': 'Basic %s' % ENCODED_TOKEN,
}


def send_jenkins_request(location, request_data=None, method='GET'):
    request_url = location if JENKINS_URL in location else JENKINS_URL + location
    response_string = ''
    if method != 'GET' and request_data is None:
        # if data is not None then POST method will be used
        # https://docs.python.org/2/library/urllib2.html#urllib2.Request
        request_data = {}
    try:
        if request_url.startswith('https'):
            # https://docs.python.org/3/library/ssl.html#ssl-security
            context = ssl.create_default_context()
            context.load_default_certs()
        else:
            context = None
        req = urllib2.Request(request_url, data=request_data, headers=HEADERS)
        urlconn = urllib2.urlopen(req, context=context)
        response_string = urlconn.read()
        response_code = urlconn.getcode()
        urlconn.close()
    except urllib2.HTTPError as e:
        response_code = e.code

    print('url: {}\ncode: {}'.format(request_url, response_code))
    return response_string


def strip_xml_tags_and_split(txt, split_by='\n'):
    result = re.sub('<[^>]*>', split_by, txt)
    print("Prinnting Result:",result)
    print("Prinnting Result:",result)
    result = [i for i in result.split(split_by) if i]
    print("Prinnting Result1:",result)
    print("Prinnting Result1:",result)
    return result
#This function strip the xml tags from the data and then split them one by one to process through send_jenkins_requestI
# text parameter for queue id example. 
#
#   <root>
#   <id>777</id>
#   <id>788</id>
#   <id>799</id>
#   </root>
#and the oputput is
#[777,788,799]

# Find downstream jobs in a queue
#
# Response is like this::
#   <root>
#   <id>777</id>
#   </root>
url = (
    '/queue/api/xml'
    '?xpath=//*[action/cause/upstreamBuild[contains(text(),%s)]]/id'
    '&wrapper=root'
    % UPSTREAM_BUILD_ID
)
data = send_jenkins_request(url)
print("Printing Data",data)
queue_ids = strip_xml_tags_and_split(data)
for qid in queue_ids:
    send_jenkins_request('/queue/cancelItem?id=%s' % qid, method='POST')


# Find downstream running jobs
#
# Response is like this::
#   <root>
#   <url>
#   http://my-jenkins.com/job/test-downstream-job/777
#   </url>
#   <url>
#   http://my-jenkins.com/job/rebuild-main-job/7
#   </url>
#   </root>
url = (
    '/computer/api/xml'
    '?tree=computer[executors[currentExecutable[url,actions[causes[*]]]]]'
    '&xpath=//*[action/cause/upstreamBuild[contains(text(),%s)]]/url'
    '&wrapper=root'
    % UPSTREAM_BUILD_ID
)
data = send_jenkins_request(url)
job_urls = strip_xml_tags_and_split(data)
for url in job_urls:
    # skip rebuilds jobs
    rebuild = '/job/%s/' % UPSTREAM_JOB_NAME
    if rebuild in url:
        print('Skip rebuild: %s' % url)
        continue
    send_jenkins_request('%sstop' % url, method='POST')
