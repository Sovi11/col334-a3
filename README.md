# col334-a3


One problem is for example if RTT is too low , and the next second the RTT becomes too high..
because our timeout is fixed, it will keep dropping the packets. because it needs 0.2 seconds now, and we are just keeping 0.02 seconds as timeout for example.

-> solutions : change the timeout time if packets are getting dropped.

0.002
-> 0.01
0.02


7-10 -> /2... 
1-7 -> reduce to 1
10 -> +1 
