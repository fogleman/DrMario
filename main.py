import wx
import random
import engine
import model
import controller

def multiplayer():
    board = model.Board(seed=2)
    board.populate()
    seed = 1#random.getrandbits(32)
    players = []
    for i in range(2):
        b = board.copy()
        j = model.Jar(1, seed)
        e = engine.Engine(seed=i) if i > 0 else None
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
    