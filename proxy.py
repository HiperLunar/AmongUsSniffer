from scapy.all import *
from netfilterqueue import NetfilterQueue
#from importlib import reload
from protocol import *
import threading
import game as AmongUsGame

game = AmongUsGame.Game()
def runGame():
    global game
    game.run()
game_thread = threading.Thread(target=runGame)

def listen(packet):
    global game
    try:
        pkt = IP(packet.get_payload())
        amongUsMsg = pkt[AmongUs]
        
        for msg in amongUsMsg.messages:
            if 'Game Data' in msg:
                gameData = msg['Game Data']
                for data in gameData.messages:
                    if Spawn in data:
                        spawn = gameData[Spawn]
                        if spawn.spawn_type == 'GAME_DATA':
                            pass
                        elif spawn.spawn_type == 'PLAYER_CONTROL':
                            pass
                        data.show2()

    except Exception as e:
        print(e)
    packet.accept()


nfqueue = NetfilterQueue()
nfqueue.bind(1, listen)
try:
    print("[*] waiting for data")
    nfqueue.run()
except KeyboardInterrupt:
    pass
