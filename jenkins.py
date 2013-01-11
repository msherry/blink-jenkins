#!/usr/bin/env python

import argparse
import ast
from itertools import count
import os
import re
import requests
import subprocess
import time

PYTHON_API_PATH = 'api/python'
INTERVAL = 30

# Ignore the 'anime' colors for these jobs -- for jobs that run periodically
# and often
JOBS_TO_IGNORE_ANIME = [
    r'cron.*'
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


class Blink(object):
    def __init__(self):
        self.color = COLORS['off']
        self.proc = None

    @property
    def proc_active(self):
        return self.proc and self.proc.poll() is None

    def set_color(self, color):
        if self.color == color and self.proc_active:
            return

        self.color = color

        if self.proc_active:
            try:
                self.proc.kill()
            except OSError:
                pass

        args = ['blink1-tool', '--rgb']
        args.append('%r' % color)
        if color.animated:
            args.extend(['--blink', str(255), '-t', '1000'])
        print args
        self.proc = subprocess.Popen(args)

COLORS = {
    'off': Color(0, 0, 0),
    'blue': Color(0, 0, 255),
    'blue_anime': Color(0, 0, 255, animated=True),
    'aborted': Color(200, 200, 200),
    'aborted_anime': Color(200, 200, 200, animated=True),
    'grey': Color(200, 200, 200),
    'grey_anime': Color(200, 200, 200, animated=True),
    'yellow': Color(255, 255, 0),
    'yellow_anime': Color(255, 255, 0, animated=True),
    'red': Color(255, 0, 0),
    'red_anime': Color(255, 0, 0, animated=True),
}


def poll_loop(blink, args):
    try:
        while True:
            poll(blink, args.host, username=args.user, password=args.password)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        blink.set_color(COLORS['off'])
    except Exception:
        blink.set_color(COLORS['off'])
        raise


def list_match(job_name, job_list):
    for pattern in job_list:
        if re.match(pattern, job_name):
            return True
        elif pattern == job_name:
            return True
    return False


def choose_color_for_job(job):
    name = job['name']

    if list_match(name, JOBS_TO_IGNORE):
        return None

    c = job['color']
    if c in ['disabled', 'aborted']:
        return None
    if list_match(name, JOBS_TO_IGNORE_ANIME):
        c = c.replace('_anime', '')

    c = COLORS[c]
    return c


def poll(blink, host, username=None, password=None):
    # TODO: os is the wrong module for this
    uri = os.path.join(host, PYTHON_API_PATH)
    auth = (username, password) if (username or password) else None
    try:
        resp = requests.get(uri, auth=auth, verify=False, timeout=30).text
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout):
        blink.set_color(COLORS['off'])
        return
    try:
        obj = ast.literal_eval(resp)
    except SyntaxError:
        # Fake response object
        obj = {
            'jobs': [],
        }
    jobs = obj['jobs']

    # Assume everything is ok
    color = COLORS['blue']
    for job in jobs:
        c = choose_color_for_job(job)
        if c and c > color:
            color = c
            print job['name']

    blink.set_color(color)


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
    cmd_args = arg_parser.parse_args()

    blinker = Blink()
    poll_loop(blinker, cmd_args)
