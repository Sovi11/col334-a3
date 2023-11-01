import socket   
import time
import re
import hashlib
import random
import matplotlib.pyplot as plt
random.seed(int(time.time()))

def get_offset(input_string):
    L = input_string.split("\n", 3)
    z = L[0]
    if(z.startswith("Offset")):
        return int(z[8:])
    print("error with input string")
    return -1

def parse_input(input_string):
    L = input_string.split("\n", 3)
    x=""
    for i in range(2, len(L)):
        x = x + L[i]
    return x



# srvr_ip = "10.17.7.134"
srvr_ip = "127.0.0.1"
srvr_port = 9801
sa = (srvr_ip, srvr_port)
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_size():
    return "SendSize\n\n"

def request_data(offset, number_of_bytes):
    message = f"Offset: {offset}\nNumBytes: {number_of_bytes}\n\n"
    return message

# RESETING.
message1 = "Reset\n\n"
udp.sendto(message1.encode(), sa)

udp.settimeout(0.0016)

#****************************************************************************************#

message1 = send_size()
T1 = time.time()
for _ in range(10):
    udp.sendto(message1.encode(), sa)
while(1):
    try:
        data, server = udp.recvfrom(2048)
        T2 = time.time() - T1
        break
    except socket.timeout:
        print(f"waiting for packet.")

time.sleep(0.5)

k = 5
strt = time.time()
flag1 = False
rtt = T2/1.2
delta= rtt/3

#****************************************************************************************#

# udp.settimeout(rtt/2)
# while(not(flag1)):
#     try:
#         message1 = send_size()
#         udp.sendto(message1.encode(), sa) 
#         data, server = udp.recvfrom(2048)
#         if((data.decode())[0] == 'O'):
#             flag1 = True
#     except socket.timeout:
#         print("SEND SIZE REQUEST TIMED OUT !!")
# print(f'THE SEND SIZE REPLY :-> {data}')

#****************************************************************************************#

def parse_size(recvd):
    s = recvd[6:]
    return int(s)

#****************************************************************************************#

Total_size = parse_size(data)
packet_size = 1448
last_packet_size = Total_size % packet_size
total_packets = ((Total_size-1)//packet_size) + 1
x = ""
queue  = [0] * total_packets
vis = [False] * total_packets
message = [""] * total_packets
for i in range(total_packets):
    queue[i] = total_packets - (i + 1)
sz = total_packets

#****************************************************************************************#

udp.settimeout(delta/(2)*k)
while(sz > k):
    window = []
    for _ in range(k):
        message1 = request_data(queue[-1] * packet_size, packet_size)
        udp.sendto(message1.encode('utf-8'), sa)
        window.append(queue[-1])
        queue.pop()
    
    sz -= k
    cnt = 0
    time.sleep(rtt/1.1)
    for _ in range(k):
        if(cnt == k):
            break
        try:
            data, server = udp.recvfrom(2048)       
            h = get_offset(data.decode('utf-8'))
            if(vis[h//packet_size] == False):
                cnt += 1
                vis[h//packet_size] = True
                message[h//packet_size] = parse_input(data.decode('utf-8'))
        except socket.timeout:
            cnt = cnt
    print(f"effficiency :-> {cnt / k}")
    for i in range(k):
        if(vis[window[i]] == False):
            queue.append(window[i])
            sz += 1

#*************************************************************#


# strt3 = time.time()
# print("hi")
# print(f"Time taken 1 =: {strt3- strt}")

while(sz > 1):
    window = []
    for _ in range(sz - 1):
        message1 = request_data(queue[-1] * packet_size, packet_size)
        udp.sendto(message1.encode('utf-8'), sa)
        window.append(queue[-1])
        queue.pop()
    cnt = 0
    time.sleep(rtt/1.5)
    x = sz - 1
    x *= 2
    for _ in range(x):
        if(cnt == sz - 1):
            break
        try:
            data, server = udp.recvfrom(2048)       
            h = get_offset(data.decode('utf-8'))
            if(vis[h//packet_size] == False):
                cnt += 1
                vis[h//packet_size] = True
                message[h//packet_size] = parse_input(data.decode('utf-8'))
        except socket.timeout:
            cnt = cnt
    for i in range(sz - 1):
        if(vis[window[i]] == False):
            queue.append(window[i])
    sz = len(queue)

# strt4 = time.time()
# print(f"Time taken 2 =: {strt4- strt}")

cnd = True
udp.settimeout(rtt)
while(cnd):
    message1 = request_data(queue[0] * packet_size, last_packet_size)
    udp.sendto(message1.encode('utf-8'), sa)
    try:
        data, server = udp.recvfrom(2048)     
        h = get_offset(data.decode('utf-8'))
        if(h == queue[0] * packet_size):
            message[h//packet_size] = parse_input(data.decode('utf-8'))
        queue.pop()
        cnd = False
        print("done")
    except socket.timeout:
        print("Time-out")
        cnd = True

strt5 = time.time()
print(f"Time taken 3 =: {strt5 - strt}")

x = ""
for i in range(total_packets):
    x = x + message[i]
res1 = hashlib.md5(x.encode())
res = res1.hexdigest()
print(res)

strt2 = time.time()
print(f"Time taken : {strt2 - strt}")

entry_num = "2021CS50596@jj"
f = f"Submit: {entry_num}\nMD5: {res}\n\n"
flag1 = False

while(not(flag1)):
    try:
        udp.sendto(f.encode(), sa)
        data, server = udp.recvfrom(2048)
        data = data.decode()
        if(data[0] != 'O'):
            flag1 = True
    except socket.timeout:
        print("send again 3")

print(data)
# print(Total_size)

# for i in range(total_packets):
#     if(vis[i] == False):
#         print(f"failed at  {i}")