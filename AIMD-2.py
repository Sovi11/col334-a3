import socket   
import time
import re
import hashlib
import random
import matplotlib.pyplot as plt
random.seed(int(time.time()))


def dbg1(x):
    print(f"LINE NUMBER = {x}")
def dbg(x):
    print(f"{x}")

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

# srvr_ip = '127.0.0.1'
srvr_ip = "10.17.7.134"
srvr_port = 9802
sa = (srvr_ip, srvr_port)
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def ask_size():
    payload_size = "SendSize\nReset\n\n".encode("utf-8")
    udp.sendto(payload_size, sa)
    udp.settimeout(0.1)
    try:
        message1, _ = udp.recvfrom(1024)
        print(f"HERER")
    except:
        print(f"JK")
        return ask_size()
    return int((str(message1)[7:][:-5]))


def request_data(offset, number_of_bytes):
    message = f"Offset: {offset}\nNumBytes: {number_of_bytes}\n\n"
    return message


udp.settimeout(0.1)
#****************************************************************************************#
message1 = ask_size()

time.sleep(0.5)
k = 10
strt = time.time()
flag1 = False
rtt = 0.013 ##0.013 vayu
# rtt = 0.0005 ## self.
delta= 0.7 * rtt

def parse_size(recvd):
    s = recvd[6:]
    return int(s)


Total_size = message1
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


while(sz > 1):   
    print(f"CURRENT BURST SIZE = {k}")
    k = min(sz - 1, k)
    window = []
    for _ in range(k):
        message1 = request_data(queue[-1] * packet_size, packet_size)
        udp.sendto(message1.encode('utf-8'), sa)
        window.append(queue[-1])
        queue.pop()
    t1 = time.time()
    sz -= k
    cnt = 0
    time.sleep(rtt)
    udp.settimeout(delta/(3)*k)
    for _ in range(k):
        if(cnt == k):
            break
        try:
            data, server = udp.recvfrom(2048)
            if(cnt == 0):
                t2 = time.time()
            h = get_offset(data.decode('utf-8'))
            if(vis[h//packet_size] == False):
                cnt += 1
                vis[h//packet_size] = True
                message[h//packet_size] = parse_input(data.decode('utf-8'))
        except socket.timeout:
            cnt = cnt
    print(f"effficiency :-> {cnt / k}")
    new_rtt = t2 - t1
    # rtt = 0.8 * new_rtt + 0.2* rtt
    print(f" rtt = {rtt}")
    next_k = k
    if(cnt/k > 0.89):
        next_k += 1
    elif(cnt/k >= 0.58):
        next_k *= 2
        next_k //= 5
        next_k = max(3, next_k)
    else:
        # adding randomisation for ffs.
        p = random.random()
        if(p < 0.3):
            next_k = 2
        else:
            time.sleep(rtt)
            next_k = 3
    for i in range(k):
        if(vis[window[i]] == False):
            queue.append(window[i])
            sz += 1
    k = next_k

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
print(Total_size)

for i in range(total_packets):
    if(vis[i] == False):
        print(f"failed at  {i}")
