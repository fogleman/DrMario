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
HUMAN = 1
DENSITY = 0.5
CEILING = 6
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
        e = engine.Engine({1: 0.38255083329257689, 2: 720.92819210954269, 3: 0.44757236906378917, 4: 6979.2565937495028, 5: 18176.733696356445, 6: 2.7646861964082938, 7: 127027.95319359133, 8: 2.4220402584369252, 9: 1717.5490514101077, 10: 14321.455663758181, 11: 1.4558893578721763})
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
    