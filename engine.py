import time
import model
import router

RECURSE = 0
DROP = 1
INFINITY = 10e9

W_HEADER = 1
W_SHIFT = 2
W_COMBO1 = 3
W_COMBO2 = 4
W_COMBO3 = 5
W_CELL = 6
W_GERM = 7
W_MATCH = 8
W_MISMATCH = 9

DEFAULT_WEIGHTS = {
    W_HEADER: 1000.0,
    W_SHIFT: 0.1,
    W_COMBO1: 1.0,
    W_COMBO2: 10.0,
    W_COMBO3: 100.0,
    W_CELL: 10.0,
    W_GERM: 50.0,
    W_MATCH: 6.0,
    W_MISMATCH: 80.0,
}

class Engine(object):
    def __init__(self, weights=None):
        self.weights = weights or DEFAULT_WEIGHTS
    def weight(self, type):
        return self.weights[type]
    def get_moves(self, the_board, the_pill, the_jar, return_score=False):
        start = time.time()
        sites = router.find_sites(the_board, the_pill)
        graph = router.Graph(the_board)
        scores = []
        for site in sites:
            pill, board = site.copy(True)
            pill.place()
            score = self.evaluate(board, pill)
            scores.append((score, site))
        if RECURSE and the_jar:
            scores.sort(reverse=True)
            new_scores = []
            for score, site in scores[:5]:
                pill, board = site.copy(True)
                pill.place()
                p = model.Pill(board, *the_jar[0])
                new_score = self.get_moves(board, p, the_jar[1:], True)
                new_scores.append((new_score, site))
            scores = new_scores
        if return_score:
            return max(score for score, site in scores)
        scores.sort(reverse=True)
        for score, site in scores:
            path = router.find_path(graph, the_pill, site)
            if path:
                break
        else:
            path = []
        if DROP:
            while path and path[-1] == model.DOWN:
                path.pop()
            path.append(model.DROP)
        end = time.time()
        duration = int((end - start) * 1000)
        #print '%d sites, %d ms.' % (len(sites), duration)
        return path
    def evaluate(self, board, pill):
        score = 0
        w, h = board.width, board.height
        combos, cells, shifts = board.reduce()
        
        # win
        if not any(cell.germ for cell in board.cells.itervalues()):
            return INFINITY
            
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
                score -= self.weight(W_HEADER)
                
        # shifts
        score -= shifts * self.weight(W_SHIFT)
        
        # combos
        ncombos = len(combos)
        if ncombos == 1:
            score += self.weight(W_COMBO1)
        if ncombos == 2:
            score += self.weight(W_COMBO2)
        if ncombos >= 3:
            score += self.weight(W_COMBO3)
            
        # counts
        for xy, cell in board.cells.iteritems():
            if cell.germ:
                score -= self.weight(W_GERM)
            else:
                score -= self.weight(W_CELL)
                
        # color changes/matches
        for x in range(w):
            germs = 0
            previous = None
            for y in range(h-1, -1, -1):
                t = h - y
                cell = board.get(x, y)
                if cell == model.EMPTY_CELL:
                    continue
                if cell.germ:
                    previous = None
                if previous:
                    if previous.color == cell.color:
                        sub = self.weight(W_MATCH)
                        sub *= (t / float(h)) + 1
                        sub *= (germs / 10.0) + 1
                        score += sub
                    else:
                        sub = self.weight(W_MISMATCH)
                        sub *= (t / float(h)) + 1
                        sub *= (germs / 10.0) + 1
                        score -= sub
                previous = cell
                if cell.germ:
                    germs += 1
                    
        return score
        
        
        
if __name__ == '__main__':
    import psyco
    psyco.full()
    engine = Engine()
    board = model.Board()
    jar = model.Jar()
    board.populate()
    count = 0
    while not board.over and not board.win:
        pill = jar.pop_pill(board)
        moves = engine.get_moves(board, pill, jar.peek())
        for move in moves:
            pill.do(move)
        pill.drop()
        pill.place()
        board.reduce()
        count += 1
        print count
        print board
        