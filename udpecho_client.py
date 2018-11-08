#! /usr/bin/env python

'''
UDP Echo Plus Client v1.0
Copyright (C) Raymond Zhou 2018
E-Mail : raymond.zhoulei at gmail.com
'''

import socket
import argparse
import signal
import time

from struct import pack_into
from struct import unpack_from
from sys import argv

socketStop = False
TestGenSN=0
TestRespSN=0
TestRespReplyFailureCount = 0
UDPEchoConfig_PacketsSend_count = 0
UDPEchoConfig_BytesSend_count = 0
UDPEchoConfig_PacketsResponse_count = 0
UDPEchoConfig_BytesResponse_count = 0
SucessfulEchoCnt=0

RoundTripPacketLoss = 0
SentPacketLoss = 0
ReceivePacketLoss = 0

def print_stat(isplus):
    if isplus:
        print 'RoundTripPacketLoss=', RoundTripPacketLoss
        print 'SentPacketLoss=', SentPacketLoss
        print 'ReceivePacketLoss=', ReceivePacketLoss

def sigint_handler(signum, frame):
    global socketStop
    socketStop = True
    print('exit signal')

def sendEchoReq(args):
    global TestGenSN
    global TestRespSN
    global RoundTripPacketLoss
    global SentPacketLoss
    global ReceivePacketLoss
    global SucessfulEchoCnt
    global TestRespReplyFailureCount

    maxSize = 2048
    minSize = 20

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'connect to server:', args.ip, args.port

    rcvdata = bytearray(maxSize+1)
    
    sock.settimeout(3)
    t = 0
    
    data_len = len(args.data)
    if not args.plus :
        print 'Send Echo Request %s to %d(%d) bytes of data.' % (args.data, data_len, data_len)
    else:
        print 'Send Echo Request %s to %d(%d) bytes of data.' % (args.data, data_len, data_len+20)

    while t < args.times:
        t+=1
        TestGenSN += 1

        if socketStop:
            print 'exists'
            sock.close()
            return

        if not args.plus :
            #print 'send msg: ',data
            sendTime=time.time()*1000
            sock.sendto(args.data,(args.ip, args.port))
            try:
                nbytes, serv = sock.recvfrom_into(rcvdata, maxSize)
                recvTime=time.time()*1000
                print 'Reply from %s: bytes=%d time=%fms' % (serv, nbytes, recvTime-sendTime)
            except Exception, err:
                print 'No reply from %s: bytes=%d' % (serv, nbytes)

        else:
            #UDP Echo plus
            #pack the data
            strfmt = '>%ds'%len(args.data)
            pack_into('>I', rcvdata, 0, TestGenSN)
            pack_into(strfmt, rcvdata, 20, args.data)
            datalen = data_len+20
            sendTime=time.time()*1000
            sock.sendto(rcvdata[:datalen],(args.ip, args.port))
            try:
                nbytes, serv = sock.recvfrom_into(rcvdata, maxSize)
                recvTime=time.time()*1000

                if nbytes == datalen:
                    RevSN, TestRespSN,RecvTimeStamp,ReplyTimeStamp,TestRespReplyFailureCount = unpack_from('>IIIII', rcvdata)
                    if RevSN != TestGenSN:
                        print 'No reply from %s: seq=%d' % (args.ip, TestGenSN)
                    else:
                        SucessfulEchoCnt+=1
                        EffectiveRTD= int(recvTime*1000)-int(sendTime*1000)-(ReplyTimeStamp - RecvTimeStamp)
                        print 'Reply from %s: seq=%d bytes=%d rtd=%dus' % (serv, RevSN, nbytes, EffectiveRTD)
                        #print 'TestRespSN,SucessfulEchoCnt,TestRespReplyFailureCount=',TestRespSN,SucessfulEchoCnt,TestRespReplyFailureCount
                else:
                    print 'Reply from %s: seq=%d bytes=%d time=%fms' % (serv, TestGenSN, nbytes, recvTime-sendTime)
            except Exception, err:
                print 'No Reply from %s: seq=%d. %s' % (args.ip, TestGenSN, err)

            pass

        time.sleep(1)

    if args.plus :
        RoundTripPacketLoss = TestGenSN - SucessfulEchoCnt
        SentPacketLoss = TestGenSN - (TestRespSN - TestRespReplyFailureCount)
        ReceivePacketLoss = RoundTripPacketLoss - SentPacketLoss

    sock.sendto('END',(args.ip, args.port))
    sock.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UDP Echo Plus Client')
    parser.add_argument('-v', '--version', action='version', version='v1.0')
    parser.add_argument('-i','--ip', required=True, type=str,
                        help='UDP Echo Plus server IP')
    parser.add_argument('-p','--port', required=True, type=int,
                        help='UDP Echo Plus server Port')
    parser.add_argument('-u', '--plus', action="store_true",
                        help='Enable UDP Echo Plus')
    parser.add_argument('-d','--data', default='Hello,world!', type=str,
                        help='package data')
    parser.add_argument('-t','--times', default=4, type=int,
                        help='times of echo request')

    args = parser.parse_args(argv[1:])

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)
    
    sendEchoReq(args)
    print_stat(args.plus)
