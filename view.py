import wx
import model
import engine
import random

SIZE = 55

SHIFT_SPEED = 100
TICK_SPEED = 500
AI_SPEED = 100

class BoardView(wx.Panel):
    def __init__(self, parent):
        super(BoardView, self).__init__(parent, -1, style=wx.WANTS_CHARS|wx.BORDER_SUNKEN)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        board = self.GetParent().board
        w = board.width * SIZE
        h = board.height * SIZE
        self.SetSize((w, h))
        self.Bind(wx.EVT_PAINT, self.on_paint)
    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        w, h = self.GetClientSize()
        dc.SetBrush(wx.BLACK_BRUSH)
        dc.DrawRectangle(0, 0, w, h)
        colors = {
            model.RED: wx.Colour(255, 0, 0),
            model.YELLOW: wx.Colour(255, 255, 0),
            model.BLUE: wx.Colour(0, 0, 255),
        }
        board = self.GetParent().board.copy()
        pill = self.GetParent().pill
        if pill:
            pill = pill.copy()
            pill.board = board
            pill.place()
        for y in range(board.height):
            for x in range(board.width):
                cell = board.get(x, y)
                if cell == model.EMPTY_CELL:
                    continue
                color = colors[cell.color]
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.WHITE_PEN)
                a, b = x*SIZE, y*SIZE
                if cell.germ:
                    dc.DrawCircle(a+SIZE/2, b+SIZE/2, SIZE/2.5)
                elif cell.connection:
                    dc.DrawRectangle(a, b, SIZE, SIZE)
                else:
                    dc.DrawRoundedRectangle(a, b, SIZE, SIZE, 10)
                    
class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, -1, 'Dr. Mario')
        self.reset()
        view = BoardView(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer(1)
        sizer.Add(view, 0, wx.ALIGN_CENTER)
        sizer.AddStretchSpacer(1)
        self.SetSizerAndFit(sizer)
        self.view = view
        self.view.Bind(wx.EVT_CHAR, self.on_char)
        self._update_timer = wx.CallLater(TICK_SPEED, self.tick)
        wx.CallLater(AI_SPEED, self.do_ai)
    def reset(self):
        self.engine = engine.Engine()
        self.board = model.Board()
        self.board.populate()
        self.new_pill()
    def new_pill(self):
        self.pill = model.Pill(self.board)
        self._rotations, self._moves = self.engine.get_moves(self.board, self.pill)
    def on_char(self, event):
        code = event.GetKeyCode()
        board = self.board
        pill = self.pill
        if not pill or board.over:
            return
        if code == wx.WXK_LEFT:
            pill.move(model.LEFT)
        if code == wx.WXK_RIGHT:
            pill.move(model.RIGHT)
        if code == wx.WXK_UP:
            pill.rotate()
        if code == wx.WXK_DOWN:
            self._update_timer.Stop()
            if pill.move(model.DOWN):
                self._update_timer = wx.CallLater(TICK_SPEED, self.tick)
            else:
                pill.drop()
                self.update()
        if code == wx.WXK_SPACE:
            self._update_timer.Stop()
            pill.drop()
            self.update()
        self.view.Refresh()
    def tick(self):
        pass #self.update()
    def update(self):
        board = self.board
        pill = self.pill
        if pill.move():
            self._update_timer = wx.CallLater(TICK_SPEED, self.tick)
        else:
            pill.place()
            self.pill = None
            self._combos = 0
            self.do_kill()
        self.view.Refresh()
    def do_ai(self):
        wx.CallLater(AI_SPEED, self.do_ai)
        board = self.board
        pill = self.pill
        if not pill:
            return
        rotations, moves = self._rotations, self._moves
        if rotations:
            pill.rotate(rotations.pop(0))
        elif moves:
            pill.move(moves.pop(0))
        else:
            self._update_timer.Stop()
            if pill.move(model.DOWN):
                self._update_timer = wx.CallLater(TICK_SPEED, self.tick)
            else:
                pill.drop()
                self.update()
        self.view.Refresh()
    def do_kill(self):
        self.view.Refresh()
        combos = self.board.kill()
        if combos:
            self._combos += combos
            wx.CallLater(SHIFT_SPEED, self.do_shift)
        else:
            if self._combos > 1:
                print '%dx Combo!!!' % self._combos
            if self.board.win or self.board.over:
                self.reset()
            else:
                self.new_pill()
            self._update_timer = wx.CallLater(TICK_SPEED, self.tick)
    def do_shift(self):
        self.view.Refresh()
        if self.board.shift():
            wx.CallLater(SHIFT_SPEED, self.do_shift)
        else:
            self.do_kill()
            
if __name__ == '__main__':
    import random
    #random.seed(0)
    
    try:
        import psyco
        psyco.full()
    except Exception:
        pass
        
    app = wx.PySimpleApp()
    frame = Frame()
    frame.Show()
    app.MainLoop()
    