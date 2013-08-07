"""
    This client do many test calls to test server
"""
import gevent 
from gevent import monkey; monkey.patch_socket()
import sys
import urllib

import getopt


argv = sys.argv[1:]
try:
    args, stuff = getopt.getopt(argv, "hs:c:g:")
    params =  dict(args)
except:
    params = dict()


_BASE_URL= "http://{}/{}"
_BASE_IP = params.get('-s') or '127.0.0.1:9000'

CONCURENT_QUERIES = int(params.get('-g',0)) or 50
CALLS_RANGE = int(params.get('-c', 0)) or 10000

print _BASE_IP

def call(num):
    """ 
    """
    try:
        resp = urllib.urlopen(_BASE_URL.format(_BASE_IP, num))
        server_info = resp.read()
        print "Request #{} was processed by {}".format(number, server_info)
    except:
        return 1

    if resp.code != 200:
        return 1
    
    return 0

def run_get():
    """
        Get queries for Load balancer test
    """
    lost = 0
    batch_count = CALLS_RANGE / CONCURENT_QUERIES
    
    for i in xrange(batch_count):
        jobs = [gevent.spawn(call, num) for num in xrange(CONCURENT_QUERIES)]
        gevent.joinall(jobs)
        lost += sum([job.value for job in jobs])
    
    # jobs = [call(num) for num in xrange(CALLS_RANGE)]
    # x = sum([job for job in jobs])
    print "{} Packets lost".format(lost)

run_get()
