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
    
PLAYERS = 1
HUMAN = 0
DENSITY = 0.75
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
        e = engine.Engine({1: 2049.9574436842422, 2: 0.031183935304790782, 3: 0.57692423335407572, 4: 9.3353612282284377, 5: 94.076534037380497, 6: 5.7387251898758969, 7: 98.209912247338352, 8: 0.069060191912076407, 9: 1.6886173198915886, 10: 0.59677181787073119, 11: 17.371924196161412})
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
    