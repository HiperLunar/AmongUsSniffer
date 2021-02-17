
import threading
import protocol
import pygame

SIZE = (1430, 800)

class Task:
    pass

class Player:
    __slots__ = [
        'id',
        'name',
        'color',
        'hat',
        'pet',
        'skin',
        'isDisconnected',
        'isImpostor',
        'isDead',
        'tasks',
        'x',
        'y'
    ]
    floatRangeX = (-40.0, 40.0)
    floatRangeY = (-40.0, 40.0)

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

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.color = (kwargs.get('color') or 0)
        self.hat = kwargs.get('hat')
        self.pet = kwargs.get('pet')
        self.skin = kwargs.get('skin')
        self.isDisconnected = (kwargs.get('isDisconnected') or False)
        self.isImpostor = (kwargs.get('isImpostor') or False)
        self.isDead = (kwargs.get('isDead') or False)
        self.tasks = kwargs.get('tasks')
        self.x = (kwargs.get('x') or 0)
        self.y = (kwargs.get('y') or 0)
    
    def render(self, surface: pygame.Surface):
        pygame.draw.circle(surface, self.COLORS[self.color], (self.x, self.y), 20)

class Game:
    __slots__ = (
        'display',
        'background',
        'running',
        'objects'
    )

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