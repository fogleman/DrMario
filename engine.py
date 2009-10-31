import time
import random
import model
import router

RECURSE = 0
INFINITY = 10e9

class Engine(object):
    def __init__(self, seed=None):
        self.rand = random.Random(seed)
    def get_moves(self, the_board, the_pill, the_jar, return_score=False):
        start = time.time()
        sites = router.find_sites(the_board, the_pill)
        graph = router.Graph(the_board)
        scores = []
        for site in sites:
            board = the_board.copy()
            pill = site.copy()
            pill.board = board
            pill.place()
            if the_jar and RECURSE:
                p = model.Pill(board, *the_jar[0])
                score = self.get_moves(board, p, the_jar[1:], True)
            else:
                score = self.evaluate(board, pill)
            scores.append((score, site))
        if return_score:
            return max(score for score, site in scores)
        scores.sort()
        scores.reverse()
        for score, site in scores:
            path = router.find_path(graph, the_pill, site)
            if path:
                break
        else:
            path = []
        end = time.time()
        duration = int((end - start) * 1000)
        print '%d sites, %d ms.' % (len(sites), duration)
        return path
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
            return INFINITY
        score -= len(germs) * 20
        
        # game over
        if board.get(w/2, 0) != model.EMPTY_CELL:
            return -INFINITY
        if board.get(w/2-1, 0) != model.EMPTY_CELL:
            return -INFINITY
            
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
        