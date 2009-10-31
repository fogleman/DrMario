import wx
import time
import random
import model
import view
import sound

TICK = 50
MOVE = 15
SHIFT = 5
ENGINE = 2
TOGGLE = 8

SOUNDS = [
    sound.Sound('./sounds/fever.mp3'),
    #sound.Sound('./sounds/chill.mp3'),
]

class Controller(object):
    def __init__(self, players):
        self.players = players
        self._counter = 0
        self._delay = 0
        self._sound = random.choice(SOUNDS)
        frame = view.MainFrame()
        for player in players:
            frame.add_player(player)
        frame.Bind(wx.EVT_CHAR, self.on_char)
        frame.Centre()
        frame.Show()
        self.frame = frame
        self.sleep()
    def update(self, player):
        combos = player.update()
        if len(combos) > 1:
            for other in self.players:
                if other == player:
                    continue
                other.rain.extend(combos)
    def refresh(self, player):
        panel = self.frame.get_panel(player)
        panel.Refresh()
    def toggle(self):
        for panel in self.frame.panels:
            panel.toggle()
            panel.Refresh()
    def sleep(self):
        duration = TICK - self._delay
        duration = max(duration, 1)
        duration = min(duration, TICK)
        wx.CallLater(duration, self.on_tick)
    def on_tick(self):
        if not self.frame:
            return
        if not self._sound.playing:
            self._sound.play()
        start = time.time()
        self._counter += 1
        states = []
        if self._counter % MOVE == 0:
            states.append(model.MOVING)
        if self._counter % SHIFT == 0:
            states.append(model.SHIFTING)
        engine = self._counter % ENGINE == 0
        for player in self.players:
            update = False
            if player.engine:
                if player.state == model.MOVING:
                    update = engine
                else:
                    update = player.state in states
            else:
                update = player.state in states
            if update:
                self.update(player)
                self.refresh(player)
        if self._counter % TOGGLE == 0:
            self.toggle()
        end = time.time()
        self._delay = int((end - start) * 1000)
        self.sleep()
    def on_char(self, event):
        code = event.GetKeyCode()
        if code == wx.WXK_LEFT:
            self.on_move(model.LEFT)
        if code == wx.WXK_RIGHT:
            self.on_move(model.RIGHT)
        if code == wx.WXK_UP:
            self.on_rotate(model.CW)
        if code == wx.WXK_DOWN:
            self.on_move(model.DOWN)
        if code == wx.WXK_SPACE:
            self.on_drop()
    def on_move(self, direction):
        for player in self.players:
            if player.engine or player.state != model.MOVING:
                continue
            success = player.pill.move(direction)
            if direction == model.DOWN and not success:
                self.update(player)
            self.refresh(player)
    def on_rotate(self, direction):
        for player in self.players:
            if player.engine or player.state != model.MOVING:
                continue
            player.pill.rotate(direction)
            self.refresh(player)
    def on_drop(self):
        for player in self.players:
            if player.engine or player.state != model.MOVING:
                continue
            player.pill.drop()
            self.update(player)
            self.refresh(player)
            