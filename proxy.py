
from protocol import *
import fakeMessage

from scapy.all import *
from netfilterqueue import NetfilterQueue

import threading
import socket

ADDRESS = ('', 21023)

class Proxy:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(ADDRESS)
        self.socket.listen(1)

        self.sniffers = []

        self.accept_thread = threading.Thread(target=self.accept)

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

    def accept(self):
        while self.running:
            conn, addr = self.socket.accept()
            self.sniffers.append(conn)
    
    def listen(self, packet):
        try:
            #get_queue()
            pkt = IP(packet.get_payload())
            for conn in self.sniffers:
                conn.send(bytes(pkt[UDP].payload))
        except KeyboardInterrupt:
            raise KeyboardInterrupt

        except Exception as e:
            print('ERROR')
            traceback.print_exc()
            print(e)
            raise KeyboardInterrupt
        packet.accept()

if __name__ == '__main__':
    proxy = Proxy()
    proxy.run()
