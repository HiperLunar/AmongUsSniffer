
import threading
import protocol
import pygame

SIZE = (1430, 800)

class Task:
    pass

COLORS = (
        (198, 17,  17 ), # 0:  Red
        (19,  46,  210), # 1:  Blue
        (17,  128, 45 ), # 2:  Green
	    (238, 84,  187), # 3:  Pink
		(240, 125, 13 ), # 4:  Orange
		(246, 246, 87 ), # 5:  Yellow
		(63,  71,  78 ), # 6:  Grey
		(215, 225, 241), # 7:  White
		(107, 47,  188), # 8:  Purple
		(113, 73,  30 ), # 9:  Brown
		(56,  255, 221), # 10: Cyan
		(80,  240, 57 ), # 11: Light_green
    )

class Game:
    __slots__ = (
        'display',
        'background',
        'running',
        'objects'
    )

    gameData = [None for x in range(10)]
    playerControl = []

    def  __init__(self):
        self.background = pygame.transform.scale(pygame.image.load('Skeld.png'), SIZE)
        self.running = False
        self.objects = []

    def tick(self):
        pass

    def render(self, surface: pygame.Surface):
        surface.blit(self.background, (0,0))
        for object in self.objects:
            object.render(surface)
        pygame.display.flip()

    def event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
    
    def createPlayer(self, player):
        self.objects.append(player)

    def getGameDataById(self, id):
        return self.gameData[id]
    
    def setGameDataById(self, data):
        if type(data) == bytes:
            data = protocol.Player(data)
        elif type(data) != protocol.Player:
            raise
        id = data.player_id
        self.gameData[id] = data
    
    def spawnPlayer(self, playerControl, networkTransform):
        playerControl.show2()
        for obj in self.objects:
            if obj[0].player_id == playerControl.player_id:
                return False
        self.objects.append((playerControl, networkTransform))
        print(self.objects)

    def run(self):
        pygame.init()
        self.display = pygame.display.set_mode(SIZE)

        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.event(event)
            self.tick()
            self.render(self.display)
    
    def stop(self):
        self.running = False

if __name__ == '__main__':
    game = Game()
    game.createPlayer(Player(
        id    = 1234,
        name  = 'REDSUS',
        color = 1
    ))
    game.run()