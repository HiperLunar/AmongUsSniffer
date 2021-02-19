
from scapy.all import *
from protocol import *

class FakeMessager:
    def __init__(self, server_addr, client_addr, **kwargs):
        self.server = server_addr
        self.client = client_addr
        self.args = kwargs

    def send(self, pkt):
        send(IP(src=self.server[0], dst=self.client[0])/UDP(sport=self.server[1], dport=self.client[1])/pkt)
        send(IP(src=self.client[0], dst=self.server[0])/UDP(sport=self.client[1], dport=self.server[1])/pkt)

    def playAnimation(self, id):
        pkt = AmongUs(type=0)/HazelMessage(tag=5)/GameData(game_id=self.args['game_id'])/GameDataTypes(tag=2)/RPC(net_id=self.args['net_id'])/id
        send(IP(src=self.server[0], dst=self.client[0])/UDP(sport=self.server[1], dport=self.client[1])/pkt)
        send(IP(src=self.client[0], dst=self.server[0])/UDP(sport=self.client[1], dport=self.server[1])/pkt)
        print('Message sent!')
    
    def setInfected(self, id):
        pass