import wx
import random
import engine
import model
import controller

PLAYERS = 1
HUMAN = 0
DENSITY = 0.5
CEILING = 5
BOARD_SEED = None
JAR_SEED = None

def multiplayer():
    board = model.Board(seed=BOARD_SEED)
    board.populate(DENSITY, CEILING)
    seed = JAR_SEED or random.getrandbits(32)
    players = []
    for i in range(PLAYERS):
        b = board.copy()
        j = model.Jar(1, seed)
        e = engine.Engine()
        if i == 0 and HUMAN:
            e = None
        player = model.Player(b, j, e)
        players.append(player)
    return players
    
def main():
    app = wx.App(False)
    players = multiplayer()
    controller.Controller(players)
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    