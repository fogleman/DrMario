import copy
import random
import itertools
import numpy

WIDTH = 8
HEIGHT = 16

LENGTH = 4
MAX_RAIN = 4

CW = 1
CCW = 2

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

EMPTY = 0
RED = 1
BLUE = 2
YELLOW = 3
COLORS = [RED, BLUE, YELLOW]

HORIZONTAL = (1, 0)
VERTICAL = (0, 1)

MOVING = 1
SHIFTING = 2
OVER = 3
WIN = 4

MOVE_NAMES = {
    UP: 'Up',
    DOWN: 'Down',
    LEFT: 'Left',
    RIGHT: 'Right',
    CW: 'CW',
    CCW: 'CCW',
}

COLOR_NAMES = {
    EMPTY: 'Empty',
    RED: 'Red',
    BLUE: 'Blue',
    YELLOW: 'Yellow',
}

class Cell(object):
    def __init__(self, color=EMPTY, germ=False, connection=None):
        self.color = color
        self.germ = germ
        self.connection = connection
    def copy(self):
        if self in (EMPTY_CELL, EXPLODE_CELL):
            return self
        return Cell(self.color, self.germ, self.connection)
        
EMPTY_CELL = Cell()
EXPLODE_CELL = Cell()

class Board(object):
    @staticmethod
    def load(path):
        with open(path, 'r') as file:
            data = file.readlines()
            return Board.loads(data)
    @staticmethod
    def loads(input):
        colors = {
            'r': RED,
            'b': BLUE,
            'y': YELLOW
        }
        input = [row.rstrip() for row in input]
        input = [row for row in input if row]
        h = len(input)
        w = max(len(row) for row in input)
        board = Board(w, h)
        for y, row in enumerate(input):
            for x, cell in enumerate(row):
                color = cell.lower()
                color = colors.get(color, EMPTY)
                germ = cell.isupper()
                if color == EMPTY:
                    cell = EMPTY_CELL
                else:
                    cell = Cell(color, germ)
                board.set(x, y, cell)
        return board
    def __init__(self, width=WIDTH, height=HEIGHT, seed=None):
        self.width = width
        self.height = height
        self.clear()
        self.rand = random.Random(seed)
    def copy(self):
        board = Board(self.width, self.height)
        board.rand.setstate(self.rand.getstate())
        for xy, cell in self.cells.iteritems():
            x, y = xy
            board.set(x, y, cell.copy())
        return board
    def clear(self):
        w, h = self.width, self.height
        self.cells = {}
        self.array = numpy.array([EMPTY_CELL] * (w * h), dtype=object).reshape(w, h)
    def get(self, x, y):
        try:
            return self.array[x, y]
        except IndexError:
            return EMPTY_CELL
    def set(self, x, y, cell):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
        self.array[x, y] = cell
        if cell == EMPTY_CELL:
            if (x, y) in self.cells:
                del self.cells[(x, y)]
        else:
            self.cells[(x, y)] = cell
    def lookup(self, cell):
        for k, v in self.cells.iteritems():
            if v == cell:
                return k
        return None
    def replace_all(self, a, b):
        for xy, cell in self.cells.items():
            if cell == a:
                x, y = xy
                self.set(x, y, b)
    def neighbor(self, cell):
        if not cell.connection:
            return None
        x, y = self.lookup(cell)
        dx, dy = cell.connection
        return self.get(x+dx, y+dy)
    @property
    def over(self):
        x = self.width / 2 - 1
        a = (x, 0)
        b = (x+1, 0)
        return self.get(*a) != EMPTY_CELL or self.get(*b) != EMPTY_CELL
    @property
    def win(self):
        return self.germ_count == 0
    @property
    def germ_count(self):
        return sum(int(cell.germ) for cell in self.cells.itervalues())
    @property
    def min_pills(self):
        combos, cells = self.find(3)
        assert not cells
        combos, cells = self.find(2)
        assert all(cell.germ for cell in cells)
        return int(self.germ_count * 1.5 - len(cells))
    def populate(self, density=0.5, ceiling=6):
        rand = self.rand
        self.clear()
        if density > 1.0:
            density = 1.0
        # pick positions
        size = self.width * (self.height - ceiling)
        count = int(size * density)
        bx = {}
        by = {}
        for x in range(self.width):
            bx[x] = 0
        for y in range(self.height - ceiling):
            by[y+ceiling] = 0
        while count:
            sx = min(bx.values())
            sy = min(by.values())
            xs = [x for x, n in bx.iteritems() if n == sx]
            ys = [y for y, n in by.iteritems() if n == sy]
            for x, y in itertools.product(xs, ys):
                if self.get(x, y) == EMPTY_CELL:
                    break
            else:
                xs = bx.keys()
                ys = by.keys()
            rand.shuffle(xs)
            rand.shuffle(ys)
            x, y = xs[0], ys[0]
            if self.get(x, y) != EMPTY_CELL:
                continue
            bx[x] += 1
            by[y] += 1
            cell = Cell(EMPTY, True)
            self.set(x, y, cell)
            count -= 1
        # assign colors
        count = len(self.cells)
        n = count / 3
        colors = [BLUE] * n + [RED] * n + [YELLOW] * n
        while len(colors) < count:
            colors.append(rand.choice(COLORS))
        rand.shuffle(colors)
        for cell, color in zip(self.cells.values(), colors):
            colors = list(COLORS)
            rand.shuffle(colors)
            colors.remove(color)
            colors.insert(0, color)
            for color in colors:
                cell.color = color
                combos, cells = self.find(LENGTH - 1)
                if not cells:
                    break
            else:
                x, y = self.lookup(cell)
                self.set(x, y, EMPTY_CELL)
        print self.min_pills
    def rain(self, colors):
        rand = self.rand
        cols = [x for x in range(self.width) if self.get(x, 0) == EMPTY_CELL]
        colors = colors[:len(cols)]
        colors = colors[:MAX_RAIN]
        combos = list(itertools.combinations(cols, len(colors)))
        rand.shuffle(combos)
        for combo in combos:
            for a, b in itertools.combinations(combo, 2):
                if abs(a - b) == 1:
                    break
            else:
                break
        else:
            combo = rand.choice(combos)
        combo = list(combo)
        rand.shuffle(combo)
        for x, color in zip(combo, colors):
            cell = Cell(color, False)
            self.set(x, 0, cell)
    def reduce(self):
        combos = []
        cells = set()
        shifts = 0
        _combos, _cells = self.kill()
        while _combos:
            combos.extend(_combos)
            cells |= _cells
            while self.shift():
                shifts += 1
            _combos, _cells = self.kill()
        return combos, cells, shifts
    def kill(self, fill=EMPTY_CELL):
        combos, cells = self.find()
        for cell in cells:
            neighbor = self.neighbor(cell)
            if neighbor:
                neighbor.connection = None
            cell.connection = None
            x, y = self.lookup(cell)
            self.set(x, y, fill)
        return combos, cells
    def shift(self):
        result = False
        for y in xrange(self.height-2, -1, -1):
            cells = []
            for x in xrange(self.width):
                cell = self.get(x, y)
                if cell.color == EMPTY:
                    continue
                if cell.germ:
                    continue
                if self.get(x, y+1) != EMPTY_CELL:
                    continue
                if cell.connection == LEFT and self.get(x-1, y+1) != EMPTY_CELL:
                    continue
                if cell.connection == RIGHT and self.get(x+1, y+1) != EMPTY_CELL:
                    continue
                cells.append((x, y, cell))
                result = True
            for x, y, cell in cells:
                self.set(x, y, EMPTY_CELL)
                self.set(x, y+1, cell)
        return result
    def find(self, length=LENGTH):
        combos = []
        horizontal = set()
        vertical = set()
        for y in xrange(self.height):
            for x in xrange(self.width):
                cell = self.get(x, y)
                if cell == EMPTY_CELL:
                    continue
                if cell not in horizontal:
                    n = self.count(x, y, HORIZONTAL)
                    if n >= length:
                        combos.append(cell.color)
                        for i in range(n):
                            horizontal.add(self.get(x+i, y))
                if cell not in vertical:
                    n = self.count(x, y, VERTICAL)
                    if n >= length:
                        combos.append(cell.color)
                        for i in range(n):
                            vertical.add(self.get(x, y+i))
        cells = horizontal | vertical
        return combos, cells
    def count(self, x, y, direction):
        dx, dy = direction
        color = self.get(x, y).color
        if color == EMPTY:
            return 0
        count = 1
        x += dx
        y += dy
        while self.get(x, y).color == color:
            count += 1
            x += dx
            y += dy
        return count
    def __str__(self):
        chars = {
            EMPTY: '..',
            RED: 'rR',
            BLUE: 'bB',
            YELLOW: 'yY',
        }
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.get(x, y)
                row.append(chars[cell.color][int(cell.germ)])
            row = ''.join(row)
            rows.append(row)
        rows.append('')
        return '\n'.join(rows)
        
class Pill(object):
    @staticmethod
    def from_key(board, key):
        p1, p2, c1, c2 = key
        pill = Pill(board, c1, c2)
        pill.pos1 = p1
        pill.pos2 = p2
        return pill
    def __init__(self, board, color1=EMPTY, color2=EMPTY):
        x = board.width / 2
        self.board = board
        self.pos1 = (x-1, 0)
        self.pos2 = (x, 0)
        self.color1 = color1 or random.choice(COLORS)
        self.color2 = color2 or random.choice(COLORS)
    def copy(self, copy_board=False):
        board = self.board.copy() if copy_board else self.board
        pill = Pill(board, self.color1, self.color2)
        pill.pos1 = self.pos1
        pill.pos2 = self.pos2
        return (pill, board) if copy_board else pill
    @property
    def key(self):
        return (self.pos1, self.pos2, self.color1, self.color2)
    @property
    def orientation(self):
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        d1 = abs(x1 - x2) == 1
        d2 = abs(y1 - y2) == 1
        if d1 and not d2:
            return HORIZONTAL
        if d2 and not d1:
            return VERTICAL
        raise Exception
    def test(self):
        board = self.board
        x, y = self.pos1
        if x < 0 or y < -1 or x >= board.width or y >= board.height:
            return False
        x, y = self.pos2
        if x < 0 or y < -1 or x >= board.width or y >= board.height:
            return False
        if board.get(*self.pos1) != EMPTY_CELL:
            return False
        if board.get(*self.pos2) != EMPTY_CELL:
            return False
        return True
    def do(self, move):
        if isinstance(move, tuple):
            return self.move(move)
        else:
            return self.rotate(move)
    def rotate(self, direction=CW, shift=True):
        #assert self.test()
        undo = CCW if direction == CW else CW
        d1 = LEFT if direction == CW else RIGHT
        d2 = RIGHT if direction == CW else LEFT
        self._rotate(direction)
        if self.test():
            return True
        if shift:
            self._move(d1)
            if self.test():
                return True
            self._move(d2, 2)
            if self.test():
                return True
            self._move(d1)
        self._rotate(undo)
        return False
    def _rotate(self, direction, times=1):
        for i in range(times):
            if direction == CW:
                if self.orientation == VERTICAL:
                    x, y = self.pos1
                    self.pos1 = (x+1, y+1)
                    self._swap()
                else:
                    x, y = self.pos1
                    self.pos1 = (x, y-1)
                    x, y = self.pos2
                    self.pos2 = (x-1, y)
            else:
                if self.orientation == VERTICAL:
                    x, y = self.pos1
                    self.pos1 = (x, y+1)
                    x, y = self.pos2
                    self.pos2 = (x+1, y)
                else:
                    x, y = self.pos2
                    self.pos2 = (x-1, y-1)
                    self._swap()
    def _swap(self):
        self.pos1, self.pos2 = self.pos2, self.pos1
        self.color1, self.color2 = self.color2, self.color1
    def drop(self):
        #assert self.test()
        while self.move(DOWN):
            pass
    def move(self, direction=DOWN):
        #assert self.test()
        undos = {
            UP: DOWN,
            DOWN: UP,
            LEFT: RIGHT,
            RIGHT: LEFT,
        }
        undo = undos[direction]
        self._move(direction)
        if self.test():
            return True
        self._move(undo)
        return False
    def _move(self, direction, times=1):
        for i in range(times):
            dx, dy = direction
            x, y = self.pos1
            self.pos1 = (x+dx, y+dy)
            x, y = self.pos2
            self.pos2 = (x+dx, y+dy)
    def place(self):
        board = self.board
        orientation = self.orientation
        connection = DOWN if orientation == VERTICAL else RIGHT
        cell1 = Cell(self.color1, False, connection)
        connection = UP if orientation == VERTICAL else LEFT
        cell2 = Cell(self.color2, False, connection)
        x, y = self.pos1
        board.set(x, y, cell1)
        x, y = self.pos2
        board.set(x, y, cell2)
    def __repr__(self):
        return str(self)
    def __str__(self):
        return str(self.key)
        
class Jar(object):
    def __init__(self, size=1, seed=None):
        self.size = size
        self.count = 0
        self.rand = random.Random(seed)
        self.queue = []
        self.populate()
    def populate(self):
        while len(self.queue) < self.size:
            self.queue.append(self.next())
    def next(self):
        c1 = self.rand.choice(COLORS)
        c2 = self.rand.choice(COLORS)
        return c1, c2
    def peek(self):
        return list(self.queue)
    def pop(self):
        result = self.queue.pop(0)
        self.count += 1
        self.populate()
        return result
    def pop_pill(self, board):
        return Pill(board, *self.pop())
    def __str__(self):
        return str(self.peek())
        
class Player(object):
    def __init__(self, board=None, jar=None, engine=None):
        self.state = MOVING
        self.board = board or Board()
        self.jar = jar or Jar()
        self.engine = engine
        self.rain = []
        self.pop_pill()
    def pop_pill(self):
        self.pill = self.jar.pop_pill(self.board)
        if self.engine:
            moves = self.engine.get_moves(self.board, self.pill, self.jar.peek())
            self._engine_data = moves
            #print ', '.join(MOVE_NAMES[move] for move in moves)
    def update(self):
        result = []
        if self.state == MOVING:
            place = False
            if self.engine:
                moves = self._engine_data
                if moves:
                    move = moves.pop(0)
                    self.pill.do(move)
                else:
                    if not self.pill.move():
                        place = True
            elif not self.pill.move():
                place = True
            if place:
                self.pill.place()
                self.pill = None
                self.state = SHIFTING
                self._combos = []
        elif self.state == SHIFTING:
            self.board.replace_all(EXPLODE_CELL, EMPTY_CELL)
            if not self.board.shift():
                combos, cells = self.board.kill(EXPLODE_CELL)
                if combos:
                    self._combos.extend(combos)
                else:
                    result = self._combos
                    self._combos = []
                    if self.board.win:
                        self.state = WIN
                    elif self.board.over:
                        self.state = OVER
                    else:
                        if self.rain:
                            self.board.rain(self.rain)
                            self.rain = []
                        else:
                            self.pop_pill()
                            self.state = MOVING
        return result
    def display(self):
        board = self.board.copy()
        if self.pill:
            pill = self.pill.copy()
            pill.board = board
            pill.place()
        return board
        w, h = board.width, board.height
        board.height += 1
        for y in range(h-1, -1, -1):
            for x in range(w):
                cell = board.get(x, y)
                board.set(x, y+1, cell)
                board.set(x, y, EMPTY_CELL)
        pill = Pill(board, *(self.jar.peek()[0]))
        pill.place()
        return board
        
        
        
if __name__ == '__main__':
    count = 0
    while True:
        board = Board()
        board.populate(1.0)
        counts = {}
        for cell in board.cells.values():
            counts[cell.color] = counts.get(cell.color, 0) + 1
        print counts
        count += 1
        print count
        print board
        