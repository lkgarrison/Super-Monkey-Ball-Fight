class PlayerData:
    def __init__(self, xpos=None, ypos=None, angle=None):
        self.xpos = xpos
        self.ypos = ypos
        self.angle = angle

class GameState:
    def __init__(self):
        # set initial angle and initial positions of the players
        initialAngle = 0

        p1_xpos = 100
        p1_ypos = 100
        self.p1_data = PlayerData(p1_xpos, p1_ypos, initialAngle)

        p2_xpos = 500
        p2_ypos = 500
        self.p2_data = PlayerData(p2_xpos, p2_ypos, initialAngle)

