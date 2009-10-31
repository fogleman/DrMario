import wx
import random
import engine
import model
import controller

try:
    import psyco
    psyco.full()
except Exception:
    pass
    
PLAYERS = 2
HUMAN = False
DENSITY = 0.5
BOARD_SEED = None
JAR_SEED = None

def multiplayer():
    board = model.Board(seed=BOARD_SEED)
    board.populate(DENSITY)
    seed = JAR_SEED or random.getrandbits(32)
    players = []
    for i in range(PLAYERS):
        b = board.copy()
        j = model.Jar(1, seed)
        e = engine.Engine(seed=i)
        if i == 0 and HUMAN:
            e = None
        player = model.Player(b, j, e)
        players.append(player)
    return players
    
def main():
    app = wx.PySimpleApp()
    players = multiplayer()
    controller.Controller(players)
    app.MainLoop()
    
if __name__ == '__main__':
    main()
    