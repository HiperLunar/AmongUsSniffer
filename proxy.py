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
        
        if amongUsMsg.type == 9:
            game.reset()
        for msg in amongUsMsg.messages:
            if 'Game Data' in msg:
                gameData = msg['Game Data']
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
                                if player:
                                    player.show()
                                else:
                                    print(f'Player with id {i} not known :(')
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
