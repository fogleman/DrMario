import model
import dijkstra

class Graph(object):
    def __init__(self, board):
        self.board = board
        self.cache = {}
    def convert(self, path):
        result = []
        pill = model.Pill.from_key(self.board, path[0])
        for key in path[1:]:
            for move in (model.DOWN, model.LEFT, model.RIGHT, model.CW, model.CCW):
                p = pill.copy()
                if not p.do(move):
                    continue
                if p.key == key:
                    result.append(move)
                    pill = p
                    break
            else:
                raise Exception
        return result
    def __getitem__(self, key):
        if key in self.cache:
            return self.cache[key]
        d = {}
        data = [
            (model.DOWN, 11),
            (model.LEFT, 10),
            (model.RIGHT, 10),
            (model.CW, 9),
            (model.CCW, 9),
        ]
        pill = model.Pill.from_key(self.board, key)
        for move, weight in data:
            p = pill.copy()
            if not p.do(move):
                continue
            d[p.key] = weight
        self.cache[key] = d
        return d
        
def find_sites(board, pill):
    def add_sites(result, x1, y1, x2, y2, c1, c2):
        result.add(((x1, y1), (x2, y2), c1, c2))
        result.add(((x1, y1), (x2, y2), c2, c1))
    sites = set()
    c1, c2 = pill.color1, pill.color2
    points = board.cells.keys()
    points.extend((x, board.height) for x in range(board.width))
    for x, y in points:
        if y < 1:
            continue
        if board.get(x, y-1) != model.EMPTY_CELL:
            continue
        if x > 0 and board.get(x-1, y-1) == model.EMPTY_CELL:
            add_sites(sites, x-1, y-1, x, y-1, c1, c2)
        if x < board.width-1 and board.get(x+1, y-1) == model.EMPTY_CELL:
            add_sites(sites, x, y-1, x+1, y-1, c1, c2)
        if y > 1 and board.get(x, y-2) == model.EMPTY_CELL:
            add_sites(sites, x, y-2, x, y-1, c1, c2)
    pills = []
    for key in sorted(sites):
        pill = model.Pill.from_key(board, key)
        pills.append(pill)
    return pills
    
def find_path(graph, start, end):
    try:
        path = dijkstra.shortestPath(graph, start.key, end.key)
        path = graph.convert(path)
        return path
    except Exception:
        return None
        