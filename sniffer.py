
from protocol import *
import game as AmongUsGame

from scapy.all import *
import threading
import socket

class Sniffer:
    def __init__(self, address):
        self.game = AmongUsGame.Game()
        self.game_thread = threading.Thread(target=self.game.run)
        self.running = False

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0.2)
        self.address = address

    def start(self):
        try:
            self.socket.connect(self.address)
            self.running = True
            self.game_thread.start()
            print('Sniffing...')
            self.listen()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(e)
            traceback.print_exc()
    
    def stop(self):
        print('Stoping!')
        self.running = False
        self.game.stop()
        self.game_thread.join()
        self.socket.close()

    def listen(self):
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    self.stop()
                    continue
                self.parse(data)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
                continue
            except socket.timeout:
                pass
            except Exception as e:
                print(e)
                traceback.print_exc()
        print('Disconnected! Stoping sniffer...')
        self.stop()

    def get_queue():
        if game.queue.empty():
            return
        else:
            i = game.queue.get()
        if i[0] == 1:
            fake = fakeMessage.FakeMessager(server, client,
                game_id=game.id,
                net_id=game.objects[0].getIds()[0])
            fake.playAnimation(i[1])
    
    def parse(self, pkt):
        try:
            amongUsMsg = AmongUs(pkt)
            #get_queue()
            
            if amongUsMsg.type == 9:
                self.game.reset()
            for msg in amongUsMsg.messages:
                if msg.tag == 9:
                    self.game.reset()
                if 'Game Data' in msg:
                    gameData = msg['Game Data']
                    self.game.id = gameData.game_id
                    for data in gameData.messages:
                        if data.tag == 1:
                            self.game.setData(data.payload)
                        if RPC in data:
                            rpc = data[RPC]
                            if rpc.RPC_call_id == 3:
                                impostors_id = rpc.payload.impostors_id
                                for i in impostors_id:
                                    print('Impostors found!')
                                    player = self.game.getGameDataById(i)
                                    player.flags |= 2
                                    if player:
                                        player.show()
                                    else:
                                        print(f'Player with id {i} not known :(')
                            elif rpc.RPC_call_id == 12:
                                c = self.game.getComponentById(ReadPackedUInt32(bytes(rpc.payload)))
                                player = self.game.getGameDataById(c.net_id)
                                player.flags |= 4
                                print(f'{player.name} is dead!')
                            elif rpc.RPC_call_id == 30:
                                payload = bytes(rpc.payload)
                                while True:
                                    if len(payload) == 0:
                                        break
                                    l = int.from_bytes(payload[0:2], 'little')
                                    player = Player(payload[2:2+l])
                                    self.game.setGameDataById(player)
                                    payload = payload[2+l:]
                                    print('PlayerUpdate!')
                        if Spawn in data:
                            spawn = data[Spawn]
                            if spawn.spawn_type == 3: # GAME_DATA
                                playersList = PlayerData(bytes(spawn.components[0].payload))
                                for player in playersList.players:
                                    self.game.setGameDataById(player)
                            elif spawn.spawn_type == 4: # PLAYER_CONTROL
                                self.game.spawnPlayer(spawn.components)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            print(e)
            traceback.print_exc()

if __name__ == '__main__':
    PROXY_ADDRESS = ('192.168.15.7', 21023)
    sniffer = Sniffer(PROXY_ADDRESS)
    sniffer.start()
