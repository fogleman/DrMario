import model
import itertools

class Engine(object):
    def get_moves(self, the_board, the_pill):
        rotation_list = [[model.CW] * n for n in range(4)]
        move_list = [[]]
        for i in range(1, the_board.width / 2 + 1):
            move_list.append([model.LEFT] * i)
            move_list.append([model.RIGHT] * i)
        best = -10e9
        result = None
        keys = set()
        for moves, rotations in itertools.product(move_list, rotation_list):
            board = the_board.copy()
            pill = the_pill.copy()
            pill.board = board
            for rotation in rotations:
                pill.rotate(rotation)
            for move in moves:
                pill.move(move)
            key = pill.key
            if key in keys:
                continue
            keys.add(key)
            pill.drop()
            pill.place()
            score = self.evaluate(board)
            if score > best:
                best = score
                result = (rotations, moves)
        return result
    def evaluate(self, board):
        score = 0
        combos = board.reduce()
        w, h = board.width, board.height
        
        cells = board.cells.values()
        germs = [cell for cell in cells if cell.germ]
        tiles = [cell for cell in cells if not cell.germ]
        
        score -= len(tiles) * 20
        score -= len(germs) * 60
        
        if combos > 1:
            score += 100
            
        for x in range(w):
            has_germ = any(board.get(x, y).germ for y in range(h))
            mult = 3 if has_germ else 1
            previous = None
            for y in range(h):
                t = h - y
                cell = board.get(x, y)
                if cell.color == model.EMPTY:
                    continue
                if previous and cell.color != previous:
                    score -= t * mult
                previous = cell.color
            previous = None
            count = 0
            for y in range(h):
                cell = board.get(x, y)
                if cell.color == model.EMPTY:
                    continue
                if previous and cell.color != previous:
                    break
                count += 1
                previous = cell.color
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
        