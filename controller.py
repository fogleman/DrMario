import wx
import time
import random
import model
import view
import sound

TICK = 10
MOVE = 750 / TICK
SHIFT = 250 / TICK
ENGINE = 150 / TICK
TOGGLE = 500 / TICK

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
            player._offset = 0
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
    def should_update(self, player):
        n = self._counter
        if player.engine and player.state == model.MOVING:
            return n % ENGINE == 0
        if player.state == model.MOVING:
            return (n + player._offset) % MOVE == 0
        if player.state == model.SHIFTING:
            return (n + player._offset) % SHIFT == 0
        return False
    def on_tick(self):
        if not self.frame:
            return
        if not self._sound.playing:
            self._sound.play()
        start = time.time()
        self._counter += 1
        for player in self.players:
            if self.should_update(player):
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
        if direction == model.DOWN:
            self.on_adjust()
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
        self.on_adjust()
        for player in self.players:
            if player.engine or player.state != model.MOVING:
                continue
            player.pill.drop()
            self.update(player)
            self.refresh(player)
    def on_adjust(self):
        for player in self.players:
            if player.engine or player.state != model.MOVING:
                continue
            player._offset = -self._counter
            