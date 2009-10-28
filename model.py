import copy
import random
import itertools

WIDTH = 8
HEIGHT = 16

LENGTH = 4

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

class Cell(object):
    def __init__(self, color=EMPTY, germ=False):
        self.color = color
        self.germ = germ
        self.connection = None
    def connect(self, other):
        self.connection = other
        other.connection = self
    def disconnect(self):
        other = self.connection
        if other:
            self.connection = None
            other.connection = None
            
EMPTY_CELL = Cell()

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
    def __init__(self, width=WIDTH, height=HEIGHT):
        self.width = width
        self.height = height
        self.cells = {}
    def copy(self):
        board = copy.deepcopy(self)
        for xy, cell in board.cells.items():
            if cell.color == EMPTY:
                board.cells[xy] = EMPTY_CELL
        return board
    def clear(self):
        self.cells = {}
    def get(self, x, y):
        return self.cells.get((x, y), EMPTY_CELL)
    def set(self, x, y, cell):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
        self.cells[(x, y)] = cell
    def lookup(self, cell):
        for k, v in self.cells.items():
            if v == cell:
                return k
        return None
    @property
    def over(self):
        x = self.width / 2 - 1
        a = (x, 0)
        b = (x+1, 0)
        return self.get(*a) != EMPTY_CELL or self.get(*b) != EMPTY_CELL
    @property
    def win(self):
        return not any(cell.germ for cell in self.cells.values())
    def populate(self, density=0.1, ceiling=6):
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
            xs = [x for x, n in bx.items() if n == sx]
            ys = [y for y, n in by.items() if n == sy]
            for x, y in itertools.product(xs, ys):
                if self.get(x, y) == EMPTY_CELL:
                    break
            else:
                xs = bx.keys()
                ys = by.keys()
            random.shuffle(xs)
            random.shuffle(ys)
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
            colors.append(random.choice(COLORS))
        random.shuffle(colors)
        for cell, color in zip(self.cells.values(), colors):
            colors = list(COLORS)
            random.shuffle(colors)
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
    def reduce(self):
        combos = 0
        count = self.kill()
        while count:
            combos += count
            while self.shift():
                pass
            count = self.kill()
        return combos
    def kill(self):
        combos, cells = self.find()
        for cell in cells:
            cell.disconnect()
            x, y = self.lookup(cell)
            self.set(x, y, EMPTY_CELL)
        return combos
    def shift(self):
        result = False
        for y in range(self.height-2, -1, -1):
            for x in range(self.width):
                cell = self.get(x, y)
                if cell == EMPTY_CELL:
                    continue
                if cell.germ:
                    continue
                if self.get(x, y+1) != EMPTY_CELL:
                    continue
                if self.get(x-1, y) == cell.connection and self.get(x-1, y+1) != EMPTY_CELL:
                    continue
                if self.get(x+1, y) == cell.connection and self.get(x+1, y+1) != EMPTY_CELL:
                    continue
                self.set(x, y, EMPTY_CELL)
                self.set(x, y+1, cell)
                result = True
        return result
    def find(self, length=LENGTH):
        combos = 0
        horizontal = set()
        vertical = set()
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get(x, y)
                if cell not in horizontal:
                    n = self.count(x, y, HORIZONTAL)
                    if n >= length:
                        combos += 1
                        for i in range(n):
                            horizontal.add(self.get(x+i, y))
                if cell not in vertical:
                    n = self.count(x, y, VERTICAL)
                    if n >= length:
                        combos += 1
                        for i in range(n):
                            vertical.add(self.get(x, y+i))
        cells = horizontal | vertical
        return combos, cells
    def count(self, x, y, direction):
        dx, dy = direction
        color = self.get(x, y).color
        if color == EMPTY:
            return 0
        count = 0
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
    def __init__(self, board, color1=EMPTY, color2=EMPTY):
        x = board.width / 2
        self.board = board
        self.pos1 = (x-1, 0)
        self.pos2 = (x, 0)
        self.color1 = color1 or random.choice(COLORS)
        self.color2 = color2 or random.choice(COLORS)
    def copy(self):
        pill = Pill(self.board)
        pill.pos1 = self.pos1
        pill.pos2 = self.pos2
        pill.color1 = self.color1
        pill.color2 = self.color2
        return pill
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
    def rotate(self, direction=CW):
        assert self.test()
        undo = CCW if direction == CW else CW
        self._rotate(direction)
        if self.test():
            return True
        self._move(LEFT)
        if self.test():
            return True
        self._move(RIGHT, 2)
        if self.test():
            return True
        self._move(LEFT)
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
        assert self.test()
        while self.move(DOWN):
            pass
    def move(self, direction=DOWN):
        assert self.test()
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
        cell1 = Cell(self.color1)
        cell2 = Cell(self.color2)
        cell1.connect(cell2)
        x, y = self.pos1
        board.set(x, y, cell1)
        x, y = self.pos2
        board.set(x, y, cell2)
    def __str__(self):
        return '%s %s' % (self.pos1, self.pos2)
        
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
        self.pop_pill()
    def pop_pill(self):
        self.pill = self.jar.pop_pill(self.board)
        if self.engine:
            self._engine_data = self.engine.get_moves(self.board, self.pill)
    def update(self):
        if self.state == MOVING:
            place = False
            if self.engine:
                rotations, moves = self._engine_data
                if rotations:
                    self.pill.rotate(rotations.pop(0))
                elif moves:
                    self.pill.move(moves.pop(0))
                else:
                    self.pill.drop()
                    place = True
            elif not self.pill.move():
                place = True
            if place:
                self.pill.place()
                self.pill = None
                self.state = SHIFTING
                self._combos = self.board.kill()
        elif self.state == SHIFTING:
            if not self.board.shift():
                combos = self.board.kill()
                if combos:
                    self._combos += combos
                else:
                    combos = self._combos
                    if combos > 1:
                        print '%dx combo!' % combos
                    if self.board.win:
                        self.state = WIN
                    elif self.board.over:
                        self.state = OVER
                    else:
                        self.pop_pill()
                        self.state = MOVING
    def display(self):
        board = self.board.copy()
        if self.pill:
            pill = self.pill.copy()
            pill.board = board
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
        