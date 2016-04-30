# Nick Ward / Luke Garrison

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet.defer import DeferredQueue

SERVER_ADDRESS = "student02.cse.nd.edu"
P2_PORT = 42202

class ServerCommandConnection(Protocol):
	def connectionMade(self):
		print "new connection made to", SERVER_ADDRESS, "port", P2_PORT
	
	def dataReceived(self, data):
		pass

	def connectionLost(self, reason):
		print "lost connection to", SERVER_ADDRESS, "port", P2_PORT

class ServerCommandConnectionFactory(ClientFactory):
	def buildProtocol(self, addr):
		return ServerCommandConnection()


if __name__ == "__main__":
    reactor.connectTCP(SERVER_ADDRESS, P2_PORT, ServerCommandConnectionFactory())
    reactor.run()
