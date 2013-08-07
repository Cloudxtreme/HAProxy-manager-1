"""
    This client do many test calls to test server
"""
import sys
import urllib

_BASE_URL= "http://{}/{}"
_BASE_IP = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1:9000'

print _BASE_IP

def run_get():
    """
        Get queries for Load balancer test
    """
    
    x = 0
    for number in xrange(10000):
        try:
            resp = urllib.urlopen(_BASE_URL.format(_BASE_IP, number))
            server_info = resp.read()
            print "Request #{} was processed by {}".format(number, server_info)
        except :
            x += 1

    print "{} Packets lost".format(x)

run_get()
