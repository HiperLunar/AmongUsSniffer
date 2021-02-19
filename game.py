
import threading
import protocol
import pygame
import scale
#from importlib import reload
import queue

SIZE = (1072, 600)
PLAYER_SHEET = pygame.image.load('Spritesheet.png')
PLAYER_SHEET.set_colorkey((255,255,255))

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

class Vector2:
    rangeX = (-40.0, +40.0)
    rangeY = (-40.0, +40.0)

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_int(x, y):
        x /= 65535
        y /= 65535
        if x < 0:
            x = 0.0
        elif x > 1.0:
            x = 1.0
        if y < 0:
            y = 0.0
        elif y > 1.0:
            y = 1.0
        
        x = Vector2.lerp(Vector2.rangeX, x)
        y = Vector2.lerp(Vector2.rangeY, y)
        return Vector2(x, y)
    
    @staticmethod
    def lerp(frange, value):
        return frange[0] + ((frange[1]-frange[0])*value)

    def to_int(self):
        pass

    def __iter__(self):
        return (self.x, self.y)
    
    def get(self):
        return (self.x, self.y)

class GameObject:
    def __init__(self, components):
        self.components = components
    
    def render(self, surface): pass

class Player(GameObject):
    IMAGE_RECT = pygame.Rect(-8, -48, 78, 103)

    def __init__(self, components):
        self.image = pygame.Surface(self.IMAGE_RECT.size)
        self.image.blit(PLAYER_SHEET.convert_alpha(), self.IMAGE_RECT)
        self.image = self.image.convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 26))
        self.myFont = pygame.font.SysFont('Comic Sans MS', 24)
        super().__init__(components)

    def getControl(self):
        return protocol.PlayerControl(bytes(self.components[0].payload))
    
    def getPysics(self):
        return bytes(self.components[1].payload)
    
    def getTransform(self):
        return protocol.NetworkTransform(bytes(self.components[2].payload))
    
    def getPos(self):
        transform = self.getTransform()
        return Vector2.from_int(transform.x_pos, transform.y_pos)
    
    def getVel(self):
        transform = self.getTransform()
        return Vector2.from_int(transform.x_vel, transform.y_vel)

    def getPlayerId(self):
        return self.getControl().player_id

    def getIds(self):
        return [component.net_id for component in self.components]
    
    def render(self, surface: pygame.Surface, playerData=None):
        pos = self.getPos().get()
        pos = (scale.x*pos[0] + scale.x0, scale.y*pos[1] + scale.y0)
        surface.blit(self.image, pos)
        if type(playerData) == protocol.Player:
            name = playerData.username.decode('utf8')
            if playerData.flags & 2:
                text = self.myFont.render(name, True, (255,0,0))
            else:
                text = self.myFont.render(name, True, (0,0,0))
            surface.blit(text, (pos[0]-10, pos[1]-10))

class Game:
    def  __init__(self):
        self.background = pygame.transform.scale(pygame.image.load('Skeld.png'), SIZE)
        self.running = False
        self.reset()
        self.queue = queue.Queue()

    def tick(self):
        pass

    def render(self, surface: pygame.Surface):
        surface.blit(self.background, (0,0))
        for obj in self.objects:
            if type(obj) == Player:
                id = obj.getPlayerId()
                data = self.getGameDataById(id)
                obj.render(surface, playerData=data)
            else:
                obj.render(surface)
        pygame.display.flip()

    def event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                self.queue.put((1, b'\x0a'))
            if event.key == pygame.K_s:
                self.queue.put((1, b'\x00'))

    def getGameDataById(self, id):
        return self.gameData[id]
    
    def setGameDataById(self, data):
        if type(data) == bytes:
            data = protocol.Player(data)
        elif type(data) != protocol.Player:
            raise
        id = data.player_id
        self.gameData[id] = data
    
    def getGameDataByName(self, name):
        for player in self.gameData:
            if player:
                if player.username == name:
                    return player

    def getComponentById(self, id):
        for obj in self.objects:
            for c in obj.components:
                if c.net_id == id:
                    return c
    
    def setComponentById(self, id, component):
        for obj in self.objects:
            for c in range(len(obj.components)):
                if obj.components[c].net_id == id:
                    obj.components[c] = component

    def setData(self, data):
        component = self.getComponentById(data.net_id)
        if component is None:
            return False
        component.length = len(data.payload)
        component.payload = data.payload
        return True


    def spawn(self, components):
        self.objects.append(GameObject(components))

    def spawnPlayer(self, components):
        playerControl = protocol.PlayerControl(bytes(components[0].payload))
        for obj in self.objects:
            if type(obj) == Player:
                if obj.getControl().player_id == playerControl.player_id:
                    return False
        self.objects.append(Player(components))
        print('Player Spawned!!!')
        return True

    def reset(self):
        self.gameData = [None for x in range(10)]
        self.objects = []
        print('Reseted!')

    def run(self):
        pygame.init()
        pygame.font.init()
        self.display = pygame.display.set_mode(SIZE)

        self.running = True
        while self.running:
            try:
                for event in pygame.event.get():
                    self.event(event)
                self.tick()
                self.render(self.display)
            except KeyboardInterrupt:
                self.stop()
                raise KeyboardInterrupt
            except Exception as e:
                print(e)
        print('END!')
    
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