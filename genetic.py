import itertools
import random
import model
import engine

def group(boards):
    result = []
    boards = [str(b).split('\n') for b in boards]
    for h in range(len(boards[0])):
        rows = [b[h] for b in boards]
        row = '  '.join(rows)
        result.append(row)
    return '\n'.join(result)
    
def run(weights, rain=False):
    players = []
    board = model.Board()
    board.populate(0.1, 6)
    seed = random.getrandbits(32)
    for w in weights:
        b = board.copy()
        j = model.Jar(1, seed)
        e = engine.Engine(w)
        p = model.Player(b, j, e)
        players.append(p)
    while True:
        import time
        time.sleep(0.1)
        germs = [p.board.germ_count for p in players]
        print germs
        print group([p.display() for p in players[:10]])
        for p in players:
            if p.jar.count > 500:
                return None
            if p.state == model.WIN:
                return players.index(p)
        for p in players:
            c = p.update()
            if rain and len(c) > 1:
                for q in players:
                    if p == q:
                        continue
                    q.rain.extend(c)
    #return None
    
def main():
    a = range(0, 100, 10)
    weights = []
    for p in a:
        w = dict(engine.DEFAULT_WEIGHTS)
        w[engine.W_GERM] = p
        weights.append(w)
    winner = run(weights)
    print winner, weights[winner]
    
def mutate(w):
    index = random.randint(1, 9)
    pct = random.randint(57, 150) / 100.0
    w[index] *= pct
    
def count_wins(w1, w2, n):
    result = 0
    for i in range(n):
        winner = run([w1, w2])
        if winner == 1:
            result += 1
    return result
    
def main2(w=None):
    w1 = dict(w) if w else engine.DEFAULT_WEIGHTS
    w2 = dict(w) if w else engine.DEFAULT_WEIGHTS
    count = 0
    while True:
        wins = count_wins(w1, w2, 3)
        if wins < 2:
            w = w1
        else:
            w = w2
        count += 1
        print 'Round %d' % count
        print 'Player %d won!' % (1 if wins < 2 else 2)
        print 'Weights: %s' % w
        for k, v in w.items():
            print '%02d: %0.3f' % (k, v)
        w1 = w
        w2 = dict(w)
        mutate(w2)
        while random.getrandbits(1):
            mutate(w2)
            
if __name__ == '__main__':
    import psyco
    psyco.full()
    main()
    