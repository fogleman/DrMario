import time
import model
import router

RECURSE = 0
INFINITY = 10e9

W_HEADER = 1
W_SHIFT = 2
W_COMBO1 = 3
W_COMBO2 = 4
W_COMBO3 = 5
W_CELL = 6
W_GERM = 7
W_CONN_CELL = 8
W_CONN_GERM = 9
W_CHANGE_CELL = 10
W_CHANGE_GERM = 11

class Engine(object):
    def __init__(self, weights=None):
        self.weights = weights or {
            W_HEADER: 100.0,
            W_SHIFT: 100.0,
            W_COMBO1: 100.0,
            W_COMBO2: 100.0,
            W_COMBO3: 100.0,
            W_CELL: 100.0,
            W_GERM: 100.0,
            W_CONN_CELL: 100.0,
            W_CONN_GERM: 100.0,
            W_CHANGE_CELL: 100.0,
            W_CHANGE_GERM: 100.0,
        }
    def weight(self, type):
        return self.weights[type]
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
                
        # top connections
        for x in range(w):
            has_germ = any(board.get(x, y).germ for y in range(h))
            previous = None
            count = 1
            for y in range(h):
                cell = board.get(x, y)
                color = cell.color
                if color == model.EMPTY:
                    continue
                if previous:
                    if color == previous:
                        count += 1
                    else:
                        break
                if cell.germ:
                    break
                previous = color
            score += count * self.weight(W_CONN_GERM if has_germ else W_CONN_CELL)
            
        # color changes
        for x in range(w):
            previous = None
            for y in range(h):
                cell = board.get(x, y)
                if cell == model.EMPTY_CELL:
                    continue
                if previous and cell.color != previous.color:
                    score -= self.weight(W_CHANGE_GERM if cell.germ else W_CHANGE_CELL)
                previous = cell if not cell.germ else None
                
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
        