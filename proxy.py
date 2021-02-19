from scapy.all import *
from netfilterqueue import NetfilterQueue
#from importlib import reload
from protocol import *
import threading
import game as AmongUsGame
import fakeMessage

server = None
client = None
game = AmongUsGame.Game()
def runGame():
    global game
    game.run()
game_thread = threading.Thread(target=runGame)

def get_queue():
    global game, server, client
    if game.queue.empty():
        return
    else:
        i = game.queue.get()
    if i[0] == 1:
        fake = fakeMessage.FakeMessager(server, client,
            game_id=game.id,
            net_id=game.objects[0].getIds()[0])
        fake.playAnimation(i[1])

def listen(packet):
    global game, server, client
    try:
        get_queue()
        pkt = IP(packet.get_payload())
        amongUsMsg = pkt[AmongUs]
        
        if amongUsMsg.type == 9:
            game.reset()
        for msg in amongUsMsg.messages:
            if msg.tag == 9:
                game.reset()
            if 'Game Data' in msg:
                gameData = msg['Game Data']
                game.id = gameData.game_id
                for data in gameData.messages:
                    if data.tag == 1:
                        game.setData(data.payload)
                    if RPC in data:
                        rpc = data[RPC]
                        if rpc.RPC_call_id == 3:
                            impostors_id = rpc.payload.impostors_id
                            for i in impostors_id:
                                print('Impostors found!')
                                player = game.getGameDataById(i)
                                player.flags |= 2
                                if player:
                                    player.show()
                                else:
                                    print(f'Player with id {i} not known :(')
                                server = (pkt.src, pkt[UDP].sport)
                                client = (pkt.dst, pkt[UDP].dport)
                                print(f"dst = '{pkt.dst}'")
                                print(f"dport = '{pkt[UDP].dport}'")
                                print(f"pkt1 = IP(src='{pkt.src}',dst='{pkt.dst}')/UDP(sport={pkt[UDP].sport}, dport={pkt[UDP].dport})/AmongUs(type=0)/HazelMessage(tag=5)/GameData(game_id='{gameData.game_id}')/GameDataTypes(tag=2)/RPC(net_id={game.objects[0].getIds()[0]})/b''")
                                print(f"pkt2 = IP(src='{pkt.dst}',dst='{pkt.src}')/UDP(sport={pkt[UDP].dport}, dport={pkt[UDP].sport})/AmongUs(type=0)/HazelMessage(tag=5)/GameData(game_id='{gameData.game_id}')/GameDataTypes(tag=2)/RPC(net_id={game.objects[0].getIds()[0]})/b''")
                                print('send(pkt1)')
                                print('send(pkt2)')
                        elif rpc.RPC_call_id == 12:
                            c = game.getComponentById(ReadPackedUInt32(bytes(rpc.payload)))
                            player = game.getGameDataById(c.net_id)
                            player.flags |= 4
                            print(f'{player.name} is dead!')
                        elif rpc.RPC_call_id == 30:
                            payload = bytes(rpc.payload)
                            while True:
                                if len(payload) == 0:
                                    break
                                l = int.from_bytes(payload[0:2], 'little')
                                player = Player(payload[2:2+l])
                                game.setGameDataById(player)
                                payload = payload[2+l:]
                                print('PlayerUpdate!')
                    if Spawn in data:
                        spawn = data[Spawn]
                        if spawn.spawn_type == 3: # GAME_DATA
                            playersList = PlayerData(bytes(spawn.components[0].payload))
                            for player in playersList.players:
                                game.setGameDataById(player)
                        elif spawn.spawn_type == 4: # PLAYER_CONTROL
                            game.spawnPlayer(spawn.components)
    except KeyboardInterrupt:
        raise KeyboardInterrupt

    except Exception as e:
        print('ERROR')
        traceback.print_exc()
        print(e)
    packet.accept()


nfqueue = NetfilterQueue()
nfqueue.bind(1, listen)
try:
    print("[*] waiting for data")
    game_thread.start()
    nfqueue.run()
except KeyboardInterrupt:
    game.stop()
    game_thread.join()
