import wx
import model

SIZE = 32

class BoardPanel(wx.Panel):
    def __init__(self, parent, player):
        super(BoardPanel, self).__init__(parent, -1, style=wx.BORDER_SUNKEN)
        self.bit = False
        self.plain = {
            model.RED: wx.Bitmap('images/red.png'),
            model.BLUE: wx.Bitmap('images/blue.png'),
            model.YELLOW: wx.Bitmap('images/yellow.png'),
        }
        self.germ1 = {
            model.RED: wx.Bitmap('images/red-germ.png'),
            model.BLUE: wx.Bitmap('images/blue-germ.png'),
            model.YELLOW: wx.Bitmap('images/yellow-germ.png'),
        }
        self.germ2 = {
            model.RED: wx.Bitmap('images/red-germ2.png'),
            model.BLUE: wx.Bitmap('images/blue-germ2.png'),
            model.YELLOW: wx.Bitmap('images/yellow-germ2.png'),
        }
        
        self.player = player
        board = player.board
        w = board.width * SIZE
        h = board.height * SIZE
        self.SetSize((w, h))
        self.Disable()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.on_paint)
    def toggle(self):
        self.bit = not self.bit
    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        w, h = self.GetClientSize()
        dc.SetBrush(wx.BLACK_BRUSH)
        dc.DrawRectangle(0, 0, w, h)
        board = self.player.display()
        for y in range(board.height):
            for x in range(board.width):
                cell = board.get(x, y)
                if cell == model.EMPTY_CELL:
                    continue
                if cell.germ:
                    if self.bit:
                        bitmap = self.germ1[cell.color]
                    else:
                        bitmap = self.germ2[cell.color]
                else:
                    bitmap = self.plain[cell.color]
                a, b = x*SIZE, y*SIZE
                dc.DrawBitmap(bitmap, a, b)
                
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
        