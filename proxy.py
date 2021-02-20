
from protocol import *
import fakeMessage

from scapy.all import *
from netfilterqueue import NetfilterQueue

import threading
import socket

OUT_ADDRESS = ('', 21023)
IN_ADDRESS = ('', 21123)

class Proxy:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(OUT_ADDRESS)
        self.socket.listen(1)

        self.ips = []

        self.sniffers = []

        self.accept_thread = threading.Thread(target=self.accept)
        self.sender_thread = threading.Thread(target=self.sender)

        self.running = False
    
    def run(self):
        try:
            self.running = True
            self.accept_thread.start()
            print('Creating NFQueue... ', end='')
            nfqueue = NetfilterQueue()
            nfqueue.bind(1, self.listen)
            print('Done!')
            print('Running proxy... ')
            nfqueue.run()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        self.running = False
        self.accept_thread.join()
        self.sender.join()

    def accept(self):
        while self.running:
            conn, addr = self.socket.accept()
            conn.settimeout(0.1)
            self.sniffers.append(conn)
    
    def listen(self, packet):
        pkt = IP(packet.get_payload())
        for conn in self.sniffers:
            try:
                conn.send(bytes(pkt[UDP].payload))
            except BrokenPipeError:
                self.sniffers.remove(conn)
        packet.accept()
    
    def sender(self):
        while self.running:
            for conn in self.sniffers:
                try:
                    data = conn.recv(2048)
                    if data:
                        send(IP(data))
                except socket.timeout:
                    pass
                


if __name__ == '__main__':
    proxy = Proxy()
    proxy.run()
