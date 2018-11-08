#! /usr/bin/env python

'''
UDP Echo Plus Server
Copyright (C) Raymond Zhou 2018
E-Mail : raymond.zhoulei at gmail.com
'''

import socket
import argparse
import signal
import time
import select

from struct import pack_into
from struct import unpack_from
from sys import argv

socketStop = False
TestRespSN = 0
TestRespReplyFailureCount = 0
UDPEchoConfig_PacketsReceived_count = 0
UDPEchoConfig_BytesReceived_count = 0
UDPEchoConfig_PacketsResponded_count = 0
UDPEchoConfig_BytesResponded_count = 0

def print_stat():
    print 'UDPEchoConfig_PacketsReceived=', UDPEchoConfig_PacketsReceived_count
    print 'UDPEchoConfig_BytesReceived=', UDPEchoConfig_BytesReceived_count
    print 'UDPEchoConfig_PacketsResponded=',UDPEchoConfig_PacketsResponded_count
    print 'UDPEchoConfig_BytesResponded=', UDPEchoConfig_BytesResponded_count

def sigint_handler(signum, frame):
    global socketStop
    socketStop = True
    print 'exit signal'

def waitForMsgs(args):
    global socketStop
    global TestRespSN
    global TestRespReplyFailureCount
    global UDPEchoConfig_PacketsReceived_count
    global UDPEchoConfig_BytesReceived_count
    global UDPEchoConfig_PacketsResponded_count
    global UDPEchoConfig_BytesResponded_count

    maxSize = 2048
    minSize = 20

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.ip, args.port))

    data = bytearray(maxSize+1)

    while not socketStop :
    
        rlist, wlist, xlist = select.select([sock],[],[],3)
    
        if [rlist,wlist,xlist] == [[],[],[]]:
            #timeout
            continue;

        if sock != rlist[0]:
            #cannot reach here..
            continue;

        nbytes, client = sock.recvfrom_into(data, maxSize)
        requestTime = int(round(time.time()*1000000))

        if nbytes == 3 :
            print client, 'has existed'
            sock.close()
            return

        if (args.source != None) :
            if(client[0] != args.source) :
                TestRespReplyFailureCount += 1
                continue #break

        if nbytes > minSize :
            if args.plus :
                revhead = unpack_from('>IIIII', data)
                TestRespSN += 1
                responseTime = int(round(time.time()*1000000))
                pack_into('>IIIII', data, 0, revhead[0], TestRespSN, (requestTime&0xFFFFFFFF), (responseTime&0xFFFFFFFF), TestRespReplyFailureCount)

                if (data[nbytes] == 0) :
                    print 'recv UDP Echo message from client %s:%s'%(client, data[minSize:nbytes])
                else:
                    print 'recv UDP Echo data %d bytes from client %s'%(nbytes,client)
            else:
                print 'recv UDP Echo data %d bytes from client %s'%(nbytes,client)
        else:
            print 'recv UDP Echo from client', client

        sock.sendto(data[:nbytes], client)

        UDPEchoConfig_PacketsReceived_count += 1
        UDPEchoConfig_BytesReceived_count += (nbytes+8)
        UDPEchoConfig_PacketsResponded_count += 1
        UDPEchoConfig_BytesResponded_count += (nbytes+8)

    if socketStop:
        print 'server exists'
        sock.close()
        return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UDP Echo Plus Server')
    parser.add_argument('-v', '--version', action='version', version='v2.0')
    parser.add_argument('-i','--ip', required=True, type=str,
                        help='UDP Echo Plus server IP')
    parser.add_argument('-p','--port', required=True, type=int,
                        help='UDP Echo Plus server Port')
    parser.add_argument('-u', '--plus', action="store_true",
                        help='Enable UDP Echo Plus')
    parser.add_argument('-s','--source', type=str,
                        help='UDP Echo Plus source IP')

    args = parser.parse_args(argv[1:])

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)
    
    waitForMsgs(args)
    print_stat()

