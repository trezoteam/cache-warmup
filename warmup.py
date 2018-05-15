#!/usr/bin/env python3
import argparse
import requests_html
import sys
from threading import BoundedSemaphore, Thread
from multiprocessing import Process
from time import sleep

parser = argparse.ArgumentParser(description="Warm up a website's page cache (initially thought for Magento 2).")
parser.add_argument('domain', type=str, help="The domain to crawl")
parser.add_argument('-m', '--max-threads', type=int, default=1, help="Maximum number of threads to spawn for requests. Default: 1")
parser.add_argument('-H', '--header', type=str, nargs='*', help="A header in the format header:value.")

args = parser.parse_args()
domain = args.domain
max_threads=10 #args.max_threads
headers = {}
if args.header:
    for header in args.header:
        l_header=header.split(':')
        headers[l_header[0].strip()] = l_header[1].strip()

session = requests_html.HTMLSession()
global stack
stack  = [domain]
global done
done = []

request_container = BoundedSemaphore(value=max_threads)

print(headers)
def request_page(current, headers, threaded=True):
    global stack
    global done
#    print(str(request_container._value))
    status_code=""
    try:
        r = session.get(current, headers=headers)
        status_code = str(r.status_code)
        urls = [link for link in r.html.absolute_links if domain in link and link not in done]
        stack = stack + urls
    except Exception as ex:
        print("==> An exception was thrown when processing this URL: " + str(ex) + '\n')
    finally:
        print("[" + status_code + "] " + current)
#        if threaded:
#            request_container.release()

while stack:
    current = stack.pop()
    done.append(current)
    #The first time cannot be threaded - we need to populate the stack
    request_page(current,headers, threaded=False)
    try:
        print("running for " + current)
#        request_container.acquire()
#        Thread(target=request_page, daemon=True, args=(current,headers)).start()
        Thread(target=request_page(current,headers), daemon=True).start()
    except ValueError:
        print("Full, skipping.")
    


