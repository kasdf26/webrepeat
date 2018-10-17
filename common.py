import urllib.parse as up
import http.client
import ssl
import argparse
import os
import json
import re
from time import sleep
import multiprocessing


chars = 'abcdefghijklmnopqrstuvwxyz' \
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
nums = '0123456789'
pwdchars = ':-_/\,'

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle


class packetvalues():
    def __init__(self):
        self.type = ''
        self.path = ''
        self.header = {}
        self.data = []  #   data format list of parameters: name=value

    def burpread(self, fp):
        # fp = open(filename, 'r')
        raw = fp.read().split("\n")
        header = []
        tmp = raw[0].split(' ')
        self.type = tmp[0]
        self.path = tmp[1]
        for line in raw:
            if ':' in line and len(line) > 4 and 'Content-Length' not in line:
                header.append(line.split(':', 1))
            elif len(line) < 4:
                break
        self.header = dict(list(header))
        if self.type == 'POST':
            if raw[-1] == '':
                raw.pop(-1)
            if '=' not in raw[-1]:
                print('[-] data format issue')
                return
            tmpdata = raw[-1].split('&')
            self.data = tmpdata




class webcoms:
    def __init__(self, proxy: bool, ssl: bool):
        self.proxy = proxy
        self.pxip = '127.0.0.1'
        self.pxport = 8080
        self.ssl = ssl
        self.host = ''

    def setup(self, url: str):
        parts = url.split('/', 3)
        self.host = parts[2]
        if 'https' in url:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            if self.proxy:
                self.conn = http.client.HTTPSConnection(self.pxip, self.pxport, context=context)
                self.conn.set_tunnel(parts[2])
            else:
                self.conn = http.client.HTTPSConnection(parts[2], context=context)

        else:
            if self.proxy:
                self.conn = http.client.HTTPConnection(self.pxip, self.pxport)
                self.conn.set_tunnel(parts[2])
            else:
                self.conn = http.client.HTTPConnection(parts[2])

    def request(self, packet: packetvalues):
        if type(self.conn) != http.client.HTTPConnection:
            print('[-] need to setup client before calling it')
            return
        if self.proxy:
            if packet.type == 'POST':
                # verify data
                data = ''
                if type(packet.data) == list:
                    tmpdata = []
                    for param in packet.data:
                        tmpdata.append(tuple(param.split('=', 1)))
                    data = up.urlencode(tmpdata)
                self.conn.request(packet.type,  packet.path, data,
                                  headers=packet.header)
            elif packet.type == 'GET':
                self.conn.request(packet.type, self.host + packet.path,
                                  headers=packet.header)
            else:
                print('[-] Unknown request type')
        else:
            if packet.type == 'POST':
                # verify data
                data = ''
                if type(packet.data) == list:
                    tmpdata = []
                    for param in packet.data:
                        tmpdata.append(tuple(param.split('=',1)))
                    data = up.urlencode(tmpdata)
                self.conn.request(packet.type, packet.path, data,
                                  headers=packet.header)
            elif packet.type == 'GET':
                self.conn.request(packet.type, packet.path,
                                  headers=packet.header)
            else:
                print('[-] Unknown request type')

class Usage:
    def __init__(self, x):
        self.running_proc = 0
        self.max_processes = x
        self.jobs = []
        self.jobtype = []
    # @staticmethod
    # def cli():
    #     command = input("\nworkflow > ")
    #     return command
    #
    # @staticmethod
    # def SetOptions(self):
    #     command = ''
    #     while (command != 'quit'):
    #         i = 1
    #         for txt in options:
    #             print("[%d] %s" % (i, txt))
    #             i += 1
    #         command = Usage.cli()
    #
    # @staticmethod
    # def printoptions(obj):
    #     i = 1
    #     for txt in obj.__dict__:
    #         if txt[0] != '_':
    #             print("[%d] %s: %s" % (i, txt, getattr(obj, txt)))
    #             i += 1

    def checkproc(self):
        rp = 0
        i = 0
        while rp != len(self.jobs) and len(self.jobs) != 0:
            if self.jobs[i].is_alive() and self.jobs[i].exitcode is None:
                rp += 1
                i += 1
                continue
            elif self.jobs[i].is_alive() and self.jobs[i].exitcode is not None :
                self.jobs[i].terminate()
            else:
                self.jobs.pop(i)
                self.jobtype.pop(i)
                rp = 0
                i = 0
        self.running_proc = rp

    def multiproc(self, func, args, stype=None):
        if stype is None:
            stype = ''
        z = 0
        while 1:
            rp = 0
            i = 0
            while rp != len(self.jobs) and len(self.jobs) != 0:
                if self.jobs[i].is_alive() and self.jobs[i].exitcode is None:
                    rp += 1
                    i += 1
                    continue
                elif self.jobs[i].is_alive() and self.jobs[i].exitcode is not None:
                    self.jobs[i].terminate()
                else:
                    self.jobs.pop(i)
                    self.jobtype.pop(i)
                    rp = 0
                    i = 0

            if rp < self.max_processes:
                #print("[INFO] {multiproc} Process now released", file=omnilog)
                break
            elif z == 60:
                #print("[INFO] {multiproc} waiting for free process, %s in use" % str(rp), file=omnilog)
                z = 0
            z += 1
            sleep(1)
        p = multiprocessing.Process(target=func, args=args)
        p.daemon = True
        p.start()
        self.jobs.append(p)
        self.jobtype.append(stype)
        rp += 1
        self.running_proc = rp