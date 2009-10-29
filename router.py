import model
import dijkstra

class Graph(object):
    def __init__(self, board):
        self.board = board
        self.cache = {}
    def convert(self, path):
        result = []
        p1, p2, c1, c2 = path[0]
        pill = model.Pill(self.board, c1, c2)
        pill.pos1 = p1
        pill.pos2 = p2
        for key in path[1:]:
            for move in (model.DOWN, model.LEFT, model.RIGHT, model.CW, model.CCW):
                p = pill.copy()
                if isinstance(move, tuple):
                    ok = p.move(move)
                else:
                    ok = p.rotate(move)
                if not ok:
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
        p1, p2, c1, c2 = key
        pill = model.Pill(self.board, c1, c2)
        pill.pos1 = p1
        pill.pos2 = p2
        d = {}
        data = [
            (model.DOWN, 1),
            (model.LEFT, 1),
            (model.RIGHT, 1),
            (model.CW, 1),
            (model.CCW, 1),
        ]
        for move, weight in data:
            p = pill.copy()
            if isinstance(move, tuple):
                ok = p.move(move)
            else:
                ok = p.rotate(move)
            if not ok:
                continue
            k = p.key
            d[k] = weight
        self.cache[key] = d
        return d
        
def _add_sites(result, x1, y1, x2, y2, c1, c2):
    p1 = (x1, y1, x2, y2, c1, c2)
    p2 = (x1, y1, x2, y2, c2, c1)
    result.add(p1)
    result.add(p2)
    
def find_sites(board, pill):
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
            _add_sites(sites, x-1, y-1, x, y-1, c1, c2)
        if x < board.width-1 and board.get(x+1, y-1) == model.EMPTY_CELL:
            _add_sites(sites, x, y-1, x+1, y-1, c1, c2)
        if y > 1 and board.get(x, y-2) == model.EMPTY_CELL:
            _add_sites(sites, x, y-2, x, y-1, c1, c2)
    pills = []
    for x1, y1, x2, y2, c1, c2 in sites:
        pill = model.Pill(board, c1, c2)
        pill.pos1 = (x1, y1)
        pill.pos2 = (x2, y2)
        pills.append(pill)
    return pills
    
def find_path(graph, start, end):
    try:
        path = dijkstra.shortestPath(graph, start.key, end.key)
        path = graph.convert(path)
        return path
    except Exception:
        return None
        