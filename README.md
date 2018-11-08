# udp-echo-plus

UDP ECHO PLUS client and server by Python  

Copyright (C) **Raymond Zhou** 2018  
E-Mail : raymond.zhoulei at gmail.com  

Follow the Broadband Forum [TR-143](http://www.broadband-forum.org/technical/download/TR-143_Amendment-1.pdf), A.1 UDP ECHO PLUS.  

## Server

Start a UDP Echo Plus server with the command  
`./udpecho_server.py -i 192.168.100.123 -p 30000 -u`  

## Client

Start a UDP Echo Plus client with the data 'Hello,world!'  
`./udpecho_client.py -i 192.168.100.123 -p 30000 -u -d "Hello,world!" -t 3`  

## Output

Server side  

> recv UDP Echo message from client ('192.168.100.83', 54142):Hellow,world!  
> recv UDP Echo message from client ('192.168.100.83', 54142):Hellow,world!  
> recv UDP Echo message from client ('192.168.100.83', 54142):Hellow,world!  
> ('192.168.100.83', 54142) has existed  
> UDPEchoConfig_PacketsReceived= 3  
> UDPEchoConfig_BytesReceived= 123  
> UDPEchoConfig_PacketsResponded= 3  
> UDPEchoConfig_BytesResponded= 123  

Client side

> connect to server: 192.168.100.123 30000  
> Send Echo Request Hellow,world! to 13(33) bytes of data.  
> Reply from ('192.168.100.123', 30000): seq=1 bytes=33 rtd=1337us  
> Reply from ('192.168.100.123', 30000): seq=2 bytes=33 rtd=1310us  
> Reply from ('192.168.100.123', 30000): seq=3 bytes=33 rtd=1886us  
> RoundTripPacketLoss= 0  
> SentPacketLoss= 0  
> ReceivePacketLoss= 0  
