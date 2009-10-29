import model

def _add_sites(result, x1, y1, x2, y2, c1, c2):
    p1 = (x1, y1, x2, y2, c1, c2)
    p2 = (x1, y1, x2, y2, c2, c1)
    result.add(p1)
    result.add(p2)
    
def _compare(p1, p2):
    if p1.pos1 != p2.pos1:
        return False
    if p1.pos2 != p2.pos2:
        return False
    if p1.color1 != p2.color1:
        return False
    if p1.color2 != p2.color2:
        return False
    return True
    
def find_sites(board, pill):
    sites = set()
    c1, c2 = pill.color1, pill.color2
    points = board.cells.keys()
    points.extend((x, board.height-1) for x in range(board.width))
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
    
def find_path(board, start, end):
    reverse = {
        model.UP: model.DOWN,
        model.LEFT: model.RIGHT,
        model.RIGHT: model.LEFT,
        model.CW: model.CCW,
        model.CCW: model.CW,
    }
    path = _find_path(board, start, end)
    if path:
        path.reverse()
        path = [reverse[n] for n in path]
        return path
    return None
    
def _get_order(start, end):
    moves = [model.UP, model.LEFT, model.RIGHT, model.CCW]#, model.CCW]
    start = start.copy()
    end = end.copy()
    order = []
    for move in moves:
        a = start.copy()
        b = end
        if isinstance(move, tuple):
            ok = a.move(move)
        else:
            ok = a.rotate(move)
        if not ok:
            continue
        if a.color1 != b.color1 or a.color2 != b.color2:
            a._swap()
        ax1, ay1 = a.pos1
        ax2, ay2 = a.pos2
        bx1, by1 = b.pos1
        bx2, by2 = b.pos2
        dist = abs(ax1-bx1) + abs(ay1-by1) + abs(ax2-bx2) + abs(ay2-by2)
        value = (dist, move)
        order.append(value)
    order.sort()
    order = [n[1] for n in order]
    return order
    
def _find_path(board, start, end, moves=None, memo=None):
    if _compare(start, end):
        return list(moves)
    moves = moves or []
    memo = memo or set()
    order = _get_order(start, end)
    for move in order:
        pill = start.copy()
        ok = False
        if isinstance(move, tuple):
            if pill.move(move):
                ok = True
        else:
            if pill.rotate(move):
                ok = True
        if not ok:
            continue
        key = pill.key
        rkey = pill.rkey
        if key in memo:# or rkey in memo:
            continue
        moves.append(move)
        memo.add(key)
        #memo.add(rkey)
        result = _find_path(board, pill, end, moves, memo)
        moves.pop()
        if result:
            return result
    return None
    