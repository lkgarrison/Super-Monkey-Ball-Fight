# Luke Garrison, Nick Ward
# 4/29/2016
# p1

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.defer import DeferredQueue
import pygame
from pygame.locals import *
import pickle
from monkey import *

SERVER_ADDRESS = "student02.cse.nd.edu"
P1_PORT = 42201
FPS = 30
TICK_RATE = 1.0 / FPS

class ServerCommandConnection(Protocol):
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(1, 50)  # repeats keyevents to support holding down keys
        self.windowSize = width, height = 800, 600
        self.screen = pygame.display.set_mode(self.windowSize)
        self.black = 0, 0, 0

        # initialize background
        self.backgroundImage = pygame.image.load('media/background.png')
        self.backgroundRect = self.backgroundImage.get_rect()
    	self.backgroundRect.center = (400, 300)

    	p1Image = pygame.image.load('media/aiai.png')
        p2Image = pygame.image.load('media/gongon.png')
        self.players = [Player(p1Image), Player(p2Image)]
        reactor.callLater(TICK_RATE, self.tick)

    def connectionMade(self):
        print "new connection made to", SERVER_ADDRESS, "port", P1_PORT
        
    def dataReceived(self, data):
        if data == "start":
            print "better start pygame now"
        else:
            gamestate = pickle.loads(data)
            #for player in self.players:
            self.players[0].update(gamestate.p1_data)


    def connectionLost(self, reason):
        print "lost connection to", SERVER_ADDRESS, "port", P1_PORT

    # checks if keypress from pygame is an arrow key or not
    def isArrowKey(self, key):
        if key == pygame.K_UP or key == pygame.K_LEFT or key == pygame.K_DOWN or key == pygame.K_RIGHT:
            return True
        else:
            return False

    def tick(self):
        self.screen.fill(self.black)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                reactor.stop() 
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                reactor.stop() 
            elif event.type == pygame.KEYDOWN: 
                if self.isArrowKey(event.key):
                    self.transport.write(str(event.key))
            elif event.type == MOUSEBUTTONDOWN:
                # if left button was clicked
                if event.button == 1:
                    self.transport.write("punch")

        # update players
        self.screen.blit(self.backgroundImage, self.backgroundRect)
        for player in self.players:
            self.screen.blit(player.image, player.rect)

        pygame.display.flip()
        reactor.callLater(TICK_RATE, self.tick)


class ServerCommandConnectionFactory(ClientFactory):
    def buildProtocol(self, addr):
        return ServerCommandConnection()

if __name__ == "__main__":
    reactor.connectTCP(SERVER_ADDRESS, P1_PORT, ServerCommandConnectionFactory())
    reactor.run()

