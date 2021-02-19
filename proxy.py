
from protocol import *
import game as AmongUsGame
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
    
    def start(self):
        try:
            print('Waiting for sniffer connection... ', end='')
            self.sniffer, self.address = self.socket.accept()
            print('Done!')
            print('Creating NFQueue... ', end='')
            nfqueue = NetfilterQueue()
            nfqueue.bind(1, self.listen)
            print('Done!')
            print('Running proxy... ')
            nfqueue.run()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        pass
    
    def listen(self, packet):
        try:
            #get_queue()
            pkt = IP(packet.get_payload())
            self.sniffer.send(bytes(pkt[UDP].payload))
        except KeyboardInterrupt:
            raise KeyboardInterrupt

        except Exception as e:
            print('ERROR')
            traceback.print_exc()
            print(e)
            raise KeyboardInterrupt
        packet.accept()


#game_server = None
#game_client = None
#game = AmongUsGame.Game()
#def runGame():
#    global game
#    game.run()
#game_thread = threading.Thread(target=runGame)
#
#def get_queue():
#    global game, game_server, game_client
#    if game.queue.empty():
#        return
#    else:
#        i = game.queue.get()
#    if i[0] == 1:
#        fake = fakeMessage.FakeMessager(game_server, game_client,
#            game_id=game.id,
#            net_id=game.objects[0].getIds()[0])
#        fake.playAnimation(i[1])
#
#def listen(packet):
#    global game, game_server, game_client, sniffer
#    try:
#        get_queue()
#        pkt = IP(packet.get_payload())
#        sniffer.send(bytes(pkt[UDP].payload))
#        amongUsMsg = pkt[AmongUs]
#        
#        if amongUsMsg.type == 9:
#            game.reset()
#        for msg in amongUsMsg.messages:
#            if msg.tag == 9:
#                game.reset()
#            if 'Game Data' in msg:
#                gameData = msg['Game Data']
#                game.id = gameData.game_id
#                for data in gameData.messages:
#                    if data.tag == 1:
#                        game.setData(data.payload)
#                    if RPC in data:
#                        rpc = data[RPC]
#                        if rpc.RPC_call_id == 3:
#                            impostors_id = rpc.payload.impostors_id
#                            for i in impostors_id:
#                                print('Impostors found!')
#                                player = game.getGameDataById(i)
#                                player.flags |= 2
#                                if player:
#                                    player.show()
#                                else:
#                                    print(f'Player with id {i} not known :(')
#                                game_server = (pkt.src, pkt[UDP].sport)
#                                game_client = (pkt.dst, pkt[UDP].dport)
#                                print(f"dst = '{pkt.dst}'")
#                                print(f"dport = '{pkt[UDP].dport}'")
#                                print(f"pkt1 = IP(src='{pkt.src}',dst='{pkt.dst}')/UDP(sport={pkt[UDP].sport}, dport={pkt[UDP].dport})/AmongUs(type=0)/HazelMessage(tag=5)/GameData(game_id='{gameData.game_id}')/GameDataTypes(tag=2)/RPC(net_id={game.objects[0].getIds()[0]})/b''")
#                                print(f"pkt2 = IP(src='{pkt.dst}',dst='{pkt.src}')/UDP(sport={pkt[UDP].dport}, dport={pkt[UDP].sport})/AmongUs(type=0)/HazelMessage(tag=5)/GameData(game_id='{gameData.game_id}')/GameDataTypes(tag=2)/RPC(net_id={game.objects[0].getIds()[0]})/b''")
#                                print('send(pkt1)')
#                                print('send(pkt2)')
#                        elif rpc.RPC_call_id == 12:
#                            c = game.getComponentById(ReadPackedUInt32(bytes(rpc.payload)))
#                            player = game.getGameDataById(c.net_id)
#                            player.flags |= 4
#                            print(f'{player.name} is dead!')
#                        elif rpc.RPC_call_id == 30:
#                            payload = bytes(rpc.payload)
#                            while True:
#                                if len(payload) == 0:
#                                    break
#                                l = int.from_bytes(payload[0:2], 'little')
#                                player = Player(payload[2:2+l])
#                                game.setGameDataById(player)
#                                payload = payload[2+l:]
#                                print('PlayerUpdate!')
#                    if Spawn in data:
#                        spawn = data[Spawn]
#                        if spawn.spawn_type == 3: # GAME_DATA
#                            playersList = PlayerData(bytes(spawn.components[0].payload))
#                            for player in playersList.players:
#                                game.setGameDataById(player)
#                        elif spawn.spawn_type == 4: # PLAYER_CONTROL
#                            game.spawnPlayer(spawn.components)
#    except KeyboardInterrupt:
#        raise KeyboardInterrupt
#
#    except Exception as e:
#        print('ERROR')
#        traceback.print_exc()
#        print(e)
#    packet.accept()
#
#nfqueue = NetfilterQueue()
#nfqueue.bind(1, listen)
#try:
#    print("[*] waiting for data")
#    game_thread.start()
#    nfqueue.run()
#except KeyboardInterrupt:
#    game.stop()
#    game_thread.join()
#

if __name__ == '__main__':
    proxy = Proxy()
    proxy.start()
