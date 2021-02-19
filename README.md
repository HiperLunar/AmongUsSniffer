# AmongUsSniffer
A sniffer using NFQUEUE to decode among us protocol

# How to use?
Redirect the among us traffic to the sniffer and use
iptables to put the udp traffic on ports 22023, 22123,
22223, 22323, 22423, 22523, 22623, 22723, 22823 and
22923 to NFQUEUE number 1
