import time
import random
import model
import router
import itertools

class Engine(object):
    def __init__(self, seed=None):
        self.rand = random.Random(seed)
    def get_moves(self, the_board, the_pill, the_jar):
        start = time.time()
        sites = router.find_sites(the_board, the_pill)
        graph = router.Graph(the_board)
        self.rand.shuffle(sites)
        best = -10e9
        result = None
        for site in sites:
            board = the_board.copy()
            pill = site.copy()
            pill.board = board
            pill.place()
            score = self.evaluate(board, pill)
            if score > best:
                path = router.find_path(graph, the_pill, site)
                if path:
                    best = score
                    result = path
        end = time.time()
        duration = int((end - start) * 1000)
        print '%d sites, %d ms.' % (len(sites), duration)
        return result
    def evaluate(self, board, pill):
        score = 0
        w, h = board.width, board.height
        combos, cells, shifts = board.reduce()
        
        # reduction
        score += 20 ** len(combos)
        score -= shifts
        
        # germ count
        germs = [cell for cell in board.cells.itervalues() if cell.germ]
        if not germs:
            score += 10000
        score -= len(germs) * 20
        
        # game over
        if board.get(w/2, 0) != model.EMPTY_CELL:
            score -= 10000
        if board.get(w/2-1, 0) != model.EMPTY_CELL:
            score -= 10000
            
        # top section
        for x in range(w):
            colors = set()
            for y in range(model.LENGTH):
                color = board.get(x, y).color
                if color != model.EMPTY:
                    colors.add(color)
            if len(colors) > 1:
                score -= 1000
                
        # color changes
        for x in range(w):
            previous = None
            germ = False
            for y in range(h-1, -1, -1):
                t = h - y
                cell = board.get(x, y)
                if cell == model.EMPTY_CELL:
                    continue
                if previous and cell.color != previous.color:
                    mult = 6 if germ else 2
                    score -= t * mult
                if cell.germ:
                    germ = True
                previous = cell
                
        # connectedness
        for x in range(w):
            previous = None
            for y in range(h):
                t = h - y
                cell = board.get(x, y)
                if cell == model.EMPTY_CELL:
                    previous = None
                    continue
                if previous and cell.color == previous.color:
                    mult = 4 if cell.germ else 2
                    score += t * mult
                previous = cell
                
        return score
        
if __name__ == '__main__':
    import psyco
    psyco.full()
    engine = Engine()
    board = model.Board()
    board.populate()
    count = 0
    while not board.over and not board.win:
        pill = model.Pill(board)
        moves = engine.get_moves(board, pill, [])
        for move in moves:
            pill.do(move)
        pill.drop()
        pill.place()
        board.reduce()
        count += 1
        print count
        print board
        