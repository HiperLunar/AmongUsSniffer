
import threading
import protocol
import pygame

SIZE = (1430, 800)

class Task:
    pass


COLORS = (
        (198, 17,  17 ), # Red
        (19,  46,  210), # Blue
        (17,  128, 45 ), # Green
	    (238, 84,  187), # Pink
		(240, 125, 13 ), # Orange
		(246, 246, 87 ), # Yellow
		(63,  71,  78 ), # Grey
		(215, 225, 241), # White
		(107, 47,  188), # Purple
		(113, 73,  30 ), # Brown
		(56,  255, 221), # Cyan
		(80,  240, 57 ), # Light_green
    )

class Game:
    __slots__ = (
        'display',
        'background',
        'running',
        'objects'
    )

    gameData = []

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
        for obj in self.objects:
            if type(obj) == GameData:
                if obj.id == id:
                    return obj

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