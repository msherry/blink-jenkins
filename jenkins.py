#!/usr/bin/env python

import argparse
import ast
from itertools import count
import os
import requests
import subprocess
import time

PYTHON_API_PATH = 'api/python'
INTERVAL = 30

# Ignore when these jobs are building -- for jobs that run periodically and
# often
JOBS_TO_IGNORE_ANIME = [

]

# Ignore these jobs completely -- for jobs that are known to be broken
JOBS_TO_IGNORE = [
    'rentmybike',
    'run_balanced_ruby_suite'
]


class Color(object):
    _ids = count(0)

    def __init__(self, red, green, blue, animated=False):
        self.red = red
        self.green = green
        self.blue = blue
        self.animated = animated
        self.id = self._ids.next()

    def __repr__(self):
        return '{},{},{}'.format(self.red, self.green, self.blue)

    def __cmp__(self, other):
        return cmp(self.id, other.id)

COLORS = {
    'off': Color(0, 0, 0),
    'blue': Color(0, 0, 255),
    'blue_anime': Color(0, 0, 255, animated=True),
    'yellow': Color(255, 255, 0),
    'yellow_anime': Color(255, 255, 0, animated=True),
    'red': Color(255, 0, 0),
    'red_anime': Color(255, 0, 0, animated=True),
}


def set_color(color):
    args = ['blink1-tool', '--rgb']
    args.append('%r' % color)
    if color.animated:
        args.extend(['--blink', str(INTERVAL)])
    print args
    subprocess.call(args)


def poll_loop(args):
    try:
        while True:
            poll(args.host, username=args.user, password=args.password)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        set_color(COLORS['off'])
    except Exception:
        set_color(COLORS['off'])
        raise


def poll(host, username=None, password=None):
    # TODO: os is the wrong module for this
    uri = os.path.join(host, PYTHON_API_PATH)
    auth = (username, password) if (username or password) else None
    resp = requests.get(uri, auth=auth, verify=False).text
    obj = ast.literal_eval(resp)
    jobs = obj['jobs']

    # Assume everything is ok
    color = COLORS['blue']
    for job in jobs:
        name = job['name']
        if name in JOBS_TO_IGNORE:
            continue
        c = job['color']
        if c in ['disabled', 'aborted']:
            continue

        if name in JOBS_TO_IGNORE_ANIME or name.startswith('cron'):
            c = c.replace('_anime', '')
        c = COLORS[c]

        if c > color:
            color = c

    set_color(color)


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host', action='store', required=True)
    parser.add_argument(
        '-u', '--user', action='store')
    parser.add_argument(
        '-p', '--password', action='store')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    poll_loop(args)
