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
        self.rand.shuffle(sites)
        best = -10e9
        result = None
        for site in sites:
            board = the_board.copy()
            pill = site.copy()
            pill.board = board
            pill.place()
            score = self.evaluate(board)
            if score > best:
                path = router.find_path(the_board, site, the_pill)
                if path:
                    best = score
                    result = path
        end = time.time()
        duration = int((end - start) * 1000)
        print '%d sites, %d ms.' % (len(sites), duration)
        return result
    def evaluate(self, board):
        score = 0
        combos, cells = board.reduce()
        score += 10 ** len(combos)
        w, h = board.width, board.height
        # germ count
        germs = [cell for cell in board.cells.values() if cell.germ]
        score -= 10 * len(germs)
        # color changes
        for x in range(w):
            has_germ = any(board.get(x, y).germ for y in range(h))
            mult = 3 if has_germ else 1
            previous = None
            for y in range(h):
                t = h - y
                color = board.get(x, y).color
                if color == model.EMPTY:
                    continue
                if previous and color != previous:
                    score -= t * mult
                previous = color
        # progressing
        for x in range(w):
            has_germ = any(board.get(x, y).germ for y in range(h))
            mult = 3 if has_germ else 1
            previous = None
            count = 0
            for y in range(h):
                color = board.get(x, y).color
                if color == model.EMPTY:
                    continue
                if previous and color != previous:
                    break
                count += 1
                previous = color
            score += count * mult
        return score
        
if __name__ == '__main__':
    import random
    random.seed(0)
    
    import psyco
    psyco.full()
    
    engine = Engine()
    board = model.Board()
    board.populate()
    count = 0
    while not board.over and not board.win:
        pill = model.Pill(board)
        rotations, moves = engine.get_moves(board, pill)
        for rotation in rotations:
            pill.rotate(rotation)
        for move in moves:
            pill.move(move)
        pill.drop()
        pill.place()
        board.reduce()
        count += 1
        print board
        print count
        