# address = "127.0.0.1"
# address = '10.17.7.218'
address = "10.17.7.134"
Port = 9801

import socket
from time import sleep as sleep
import time
import threading
import time
import random
import hashlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def clean_buffer():
    client_socket.settimeout(0.1)
    try:
        message, _ = client_socket.recvfrom(2048)
        clean_buffer()
    except:
        return


def ask_size():
    payload_size = "SendSize\nReset\n\n".encode("utf-8")
    client_socket.sendto(payload_size, (address, Port))
    client_socket.settimeout(0.1)
    try:
        message, _ = client_socket.recvfrom(1024)
    except:
        return ask_size()
    return int((str(message)[7:][:-5]))


def send_offset_backoff(offset, num_bytes, backoff):
    message_send = f"Offset: {offset}\nNumBytes: {num_bytes}\n\n".encode("utf-8")
    client_socket.sendto(message_send, (address, Port))
    client_socket.settimeout(backoff)
    try:
        message, _ = client_socket.recvfrom(2048)
    except:
        message = "".encode()
    return str(message.decode())


def submit_final(hex_final):
    submit_message = f"Submit: 2021CS10075@ok\nMD5: {hex_final}\n\n".encode()
    client_socket.sendto(submit_message, (address, Port))
    client_socket.settimeout(0.1)
    try:
        message, addr = client_socket.recvfrom(2048)
        assert message.decode()[0:6] == "Result"
    except:
        submit_final(hex_final)
    return message.decode()


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def cleanup_squished(message_str):
    if len(message_str) == 0:
        return None
    list_string = message_str.split("\n", 3)
    if list_string[3][0] == "\n" and list_string[2] == "Squished":
        list_string[3] = list_string[3][1:]
    try:
        assert int(list_string[1][-4:]) == len(list_string[3])
    except:
        return None
    try:
        return list_string
    except:
        return None


def send_burst_squished(start, burst_size, rtt):
    squish_cnt = 0
    cnt = start
    wrong_cnt = 0
    things_rec = 0
    rtt_time_sum = 0
    rtt_sample_cnt = 0
    while (things_rec < burst_size) and (len(set_received) < number_of_things_to_ask):
        random_ele = cnt % number_of_things_to_ask
        if random_ele in set_received:
            cnt += 1
            continue
        start_time = time.time()
        temp_thing = cleanup_squished(
            send_offset_backoff(
                1448 * random_ele,
                min(1448, size_of_string - 1448 * random_ele),
                4 * rtt,
            )
        )
        if temp_thing is None:
            wrong_cnt += 1
            continue
        else:
            rtt_time_sum += time.time() - start_time
            rtt_sample_cnt += 1
            if temp_thing[2] == "Squished":
                squish_cnt += 1
            index_reverse = int(str(temp_thing[0])[7:]) // 1448
            if index_reverse == (random_ele):
                things_rec += 1
                cnt += 1
            set_received.add(index_reverse)
            list_number_of_things_ask[index_reverse] = temp_thing[3]
    if wrong_cnt > 0.1 * burst_size:
        if rtt_sample_cnt == 0:
            return [False, cnt, squish_cnt, 0, rtt_sample_cnt]
        else:
            return [
                False,
                cnt,
                squish_cnt,
                rtt_time_sum / rtt_sample_cnt,
                rtt_sample_cnt,
            ]

    else:
        if rtt_sample_cnt == 0:
            return [True, cnt, squish_cnt, 0, rtt_sample_cnt]
        else:
            return [
                True,
                cnt,
                squish_cnt,
                rtt_time_sum / rtt_sample_cnt,
                rtt_sample_cnt,
            ]


rtt = 0.02
clean_buffer()
size_of_string = ask_size()
number_of_things_to_ask = (size_of_string + 1447) // 1448
list_number_of_things_ask = [-1 for _ in range(number_of_things_to_ask)]
start_time = time.time()
set_received = set()
cnt = 0
RTT_times = []
cnt_array = []
burst_size_init = 4
start_init = 0
incremental_rate = 1
burst_size_list = []
squish_cnt = 0
total_rtt_cnt = 2
while len(set_received) < number_of_things_to_ask:
    [x, y, z, rtt_avg, rtt_cnt] = send_burst_squished(start_init, burst_size_init, rtt)
    rtt = ((rtt * total_rtt_cnt) + (rtt_avg * rtt_cnt)) / (total_rtt_cnt + rtt_cnt)
    total_rtt_cnt += rtt_cnt
    squish_cnt += z
    burst_size_list.append(burst_size_init)
    if x:
        burst_size_init += incremental_rate
    else:
        burst_size_init = (burst_size_init) // 2
        if burst_size_init <= 1:
            time.sleep((max(2 * rtt, 0.01)))
    start_init = y
    time.sleep(max((burst_size_init + 1) * rtt, 0.006))
string_submitted = "".join(list_number_of_things_ask)
result = hashlib.md5(string_submitted.encode())
print(submit_final(result.hexdigest()))
print(f"Number of squishes are {squish_cnt} ")
clean_buffer()