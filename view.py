import wx
import model

SIZE = 30

class BoardPanel(wx.Panel):
    def __init__(self, parent, player):
        super(BoardPanel, self).__init__(parent, -1, style=wx.BORDER_SUNKEN)
        self.player = player
        board = player.board
        w = board.width * SIZE
        h = board.height * SIZE
        self.SetSize((w, h))
        self.Disable()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
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
        board = self.player.display()
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
                    dc.DrawRectangle(a, b, SIZE-1, SIZE-1)
                else:
                    dc.DrawRoundedRectangle(a, b, SIZE-1, SIZE-1, 10)
                    
class MainFrame(wx.Frame):
    def __init__(self):
        super(MainFrame, self).__init__(None, -1, 'Dr. Mario')
        panel = wx.Panel(self, -1)
        self.players = []
        self.panels = []
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = panel
        panel.SetSizer(self.sizer)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
    def add_player(self, player):
        panel = BoardPanel(self.panel, player)
        self.sizer.Add(panel, 0, wx.ALL, 10)
        self.Fit()
        self.players.append(player)
        self.panels.append(panel)
    def get_panel(self, player):
        index = self.players.index(player)
        return self.panels[index]
        