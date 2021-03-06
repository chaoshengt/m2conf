#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'mhohai'
"""
For GoAgent choice fast ip
"""

import re
import threading
import subprocess

#compile regex
"""
I'm using Ubuntu, re.compile by ping and w3m stdout.
Other system should change it to compare your PC.
please: $sudo apt-get install w3m
"""
re_avg_time = re.compile(r'\d+/(\d+)', re.M)
re_loss_percent = re.compile(r'(\d+)%', re.M)
re_find_dns_name = re.compile(r'dNSName=([^:]+)', re.M)

#ip_set = [('0.0.0', min, max), ]
#ip_set = [('203.208.46', 140, 145), ]
from GCC import ip_set  # setting ip set first.

ip_list = []


def find_host(ip):
    w3m_cmd_command = ('w3m', 'https://'+ip)
    w3m_https = subprocess.Popen(w3m_cmd_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    w3m_https.wait()
    w3m_message = w3m_https.stdout.read()
    host_name = re_find_dns_name.search(w3m_message)
    host_name = host_name and host_name.group(1) or None

    return host_name


class Ping(threading.Thread):
    def __init__(self, ip_address):
        threading.Thread.__init__(self)
        self.ip_address = ip_address

    def run(self):
        # ping IP Address, add 0% loss to ip_list
        ping_cmd_command = ('ping', '-c 4', self.ip_address)
        ping_cmd = subprocess.Popen(ping_cmd_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        ping_cmd.wait()

        ping_cmd_echo = ping_cmd.stdout.read()
        loss_percent = re_loss_percent.search(ping_cmd_echo)
        loss_percent = int(loss_percent.group(1)) if loss_percent is not None else 200
        avg_time = re_avg_time.search(ping_cmd_echo)
        avg_time = avg_time and int(avg_time.group(1)) or 0

        host_name = find_host(self.ip_address)

        # wait mutex and add to list
        global lock
        try:
            lock.acquire()
            ip_list.append((loss_percent, avg_time, self.ip_address, host_name))
        except:
            pass
        finally:
            lock.release()


def list_ping(_set):
    for _ in _set:
        for i in range(_[1], _[2]):
            ping_thread = Ping('%s.%d' % (_[0], i))
            ping_thread.start()

    print threading.activeCount()-2, 'threading working...'
    while threading.activeCount() > 2:
        pass
    
    ip_list.sort()
    # I want print by fast!!!  this doesn't work.
    print '%-6s%-4s%-16s%s' % ('loss%', 'avg', 'IP Address', 'dNSName')
    for ip in ip_list:
        print '%-6s%-4s%-16s%s' % ip


if __name__ == '__main__':
    global lock
    lock = threading.Lock()
    list_ping(ip_set)
