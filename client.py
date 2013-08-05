"""
    This client do many test calls to test server
"""
import urllib


def run_get():
    """
        Get queries for Load balancer test
    """
    BASE_URL = "http://127.0.0.1:9000/{}"
    x = 0
    for number in xrange(10000):
        try:
            resp = urllib.urlopen(BASE_URL.format(number))
            server_info = resp.read()
            print "Request #{} was processed by {}".format(number, server_info)
        except :
            x += 1

    print x

run_get()
