#!/usr/bin/env python3
import argparse
import requests_html
import sys

parser = argparse.ArgumentParser(description="Warm up a website's page cache (initially thought for Magento 2).")
parser.add_argument('domain', type=str, help="The domain to crawl")
parser.add_argument('-M', '--max-requests', type=int, help="Maximum number of requests to perform")
parser.add_argument('-H', '--header', type=str, nargs='*', help="A header in the format header:value.")

args = parser.parse_args()
domain = args.domain
max_reqs = args.max_requests
headers={}
if args.header:
    for header in args.header:
        l_header=header.split(':')
        headers[l_header[0].strip()] = l_header[1].strip()

session = requests_html.HTMLSession()
stack = [domain]
done = []

while stack and len(done) < max_reqs:
    current = stack.pop()
    done.append(current)
    status_code=""
    print(current)
    try:
        r = session.get(current, headers=headers)
        status_code = str(r.status_code)
        urls = [link for link in r.html.absolute_links if domain in link and link not in done]
        stack = stack + urls
    except Exception as ex:
        print("==> An exception was thrown when processing this URL: " + str(ex) + '\n')
    finally:
        sys.stdout.write("\033[F")
        print("[" + status_code + "] " + current)
