# Super Monkey Ball Fight
![](https://github.com/lkgarrison/Super-Monkey-Ball-Fight/blob/master/media/actionShot.png)

Super Monkey Ball Fight is 2D network-based fighting game based on the
Monkey Fight minigame from Super Monkey Ball. In this game, players
attempt to knock each other off the battlefield by running into each
other or dropping bananas to have the other player slip off the edge.


## Running

Super Monkey Ball Fight is a python-based game using python version 2.6.
Additionally, the users must have the Twisted and PyGame libraries in
order to connect and run the game. To start the game, one person can
start the server, used for updating the changes to the game state and
distributing the updates to the players, by executing the command:
python server.py. Once the server is running, the players can connect
by each running a player script. For instance, the first player can
run the command: python p1.py and the second player can run the
command: python p2.py. Once both players are connected the game will
begin.


## Game Play

The game starts once both players have successfully connected to the
server. Once the first player connects, the player will be sent to
a waiting screen while waiting for another player to join the game.
To start, player 1 will spawn in the upper left corner of the
battlefield, while player 2 will spawn in the lower right corner of
the battlefield. The objective of the game is to knock your opponent
off of the grid. The opponent is knocked backwards by running your
character into your opponent. To move your character, use the arrow
keys to move in the desired direction. By holding two arrow keys at
once, a player can move diagonally. A player has a stock of bananas
that increments every few seconds. If a player has any bananas and
is moving, pressing the spacebar will drop a banana behind the
player. If a player collides with a banana, then the player will be
temporarily stuck sliding in the direction they were moving when
the collision occurred. The game will continue until one player has
been knocked off the battlefield. Once a player has been knocked
off the map, both players' game windows will close and the players
are notified of the winner within their terminal window. Players
can also quit early by exiting from the game window or by pressing
the escape key, but either method will end the current game. Once
a game is over, another round can be initiated once both players 
run their scripts again and reconnect, as long as the server is 
still running. If the server connection to either client is lost, 
then the game will end and the server may need to be restarted
before playing again.
