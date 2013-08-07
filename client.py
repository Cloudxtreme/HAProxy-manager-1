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
    args, stuff = getopt.getopt(argv, "hs:c:")
    params =  dict(args)
except:
    params = dict()


_BASE_URL= "http://{}/{}"
_BASE_IP = params.get('-s') or '127.0.0.1:9000'

CALLS_RANGE = params.get('-c') or 10000

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

    return 0

def run_get():
    """
        Get queries for Load balancer test
    """
    
    jobs = [gevent.spawn(call, num) for num in xrange(CALLS_RANGE)]
    gevent.joinall(jobs)
    x = sum([job.value for job in jobs])
    # jobs = [call(num) for num in xrange(CALLS_RANGE)]
    # x = sum([job for job in jobs])
    print "{} Packets lost".format(x)

run_get()
