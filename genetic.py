import random
import model
import engine

def mutate(w):
    index = random.randint(1, 11)
    pct = random.randint(57, 150) / 100.0
    w[index] *= pct
    
def run(w1, w2):
    board = model.Board()
    board.populate(0.25, 6)
    seed = random.getrandbits(32)
    b1 = board.copy()
    b2 = board.copy()
    j1 = model.Jar(1, seed)
    j2 = model.Jar(1, seed)
    e1 = engine.Engine(w1)
    e2 = engine.Engine(w2)
    p1 = model.Player(b1, j1, e1)
    p2 = model.Player(b2, j2, e2)
    while True:
        if p1.state == model.OVER or p2.state == model.WIN:
            winner = 2
            break
        if p2.state == model.OVER or p1.state == model.WIN:
            winner = 1
            break
        if p1.jar.count > 500 or p2.jar.count > 500:
            winner = 1
            break
        c1 = p1.update()
        c2 = p2.update()
        if len(c1) > 1:
            p2.rain.extend(c1)
        if len(c2) > 1:
            p1.rain.extend(c2)
    return winner, p1, p2
    
def count_wins(w1, w2, n):
    result = 0
    for i in range(n):
        winner, p1, p2 = run(w1, w2)
        print p1.display()
        print p2.display()
        if winner == 2:
            result += 1
    return result, p1, p2
    
def main(w=None):
    w1 = dict(w) if w else None
    w2 = dict(w) if w else None
    count = 0
    while True:
        #winner, p1, p2 = run(w1, w2)
        wins, p1, p2 = count_wins(w1, w2, 3)
        if wins < 2:
            w = p1.engine.weights
        else:
            w = p2.engine.weights
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
    #main({1: 3656.9999999999995, 2: 0.077000000000000013, 3: 5.0, 4: 705.96000000000004, 5: 1000.0, 6: 56.999999999999993, 7: 500.0, 8: 1.3100000000000001, 9: 6.75, 10: 10.0, 11: 60.5})
    #main({1: 1130.1155747666612, 2: 0.0084124819289585831, 3: 2.7659351344880556, 4: 100.0, 5: 349.71231004091931, 6: 62.680426786886052, 7: 74.121333216605166, 8: 1.2771774460168404, 9: 2.5912113404829156, 10: 0.24022515614909506, 11: 22.660416482106413})
    #main({1: 549.66180053406265, 2: 0.031126274273164039, 3: 19.674340585763758, 4: 131.21629986816004, 5: 198.131956554417, 6: 64.47300535338988, 7: 41.17366926464441, 8: 0.53984737718758669, 9: 3.6170690618024377, 10: 0.10678763218493051, 11: 10.584675556630014, 12: 0.001})
    #main({1: 49.149931726646152, 2: 0.017130774420792902, 3: 1.0, 4: 2.0, 5: 3.0, 6: 6.9442686050442175, 7: 4.4770785257079551, 8: 0.075354794784102716, 9: 0.19388152165979275, 10: 0.11081504671693153, 11: 2.0851097840549508, 12: 0.00013972679736027439})
    #main({1: 49.850121654023958, 2: 0.012486792783060155, 3: 1.0, 4: 2.7359999999999998, 5: 3.8106, 6: 2.0451732131162244, 7: 2.418267103189998, 8: 0.052409259772343439, 9: 0.15122758689463836, 10: 0.15146200585270203, 11: 2.7314938171119856})
    #main({1: 0.28774612096797342, 2: 0.085269449378678461, 3: 0.096832656010876428, 4: 1.5835149516872495, 5: 1.4176874856862887, 6: 0.81089829615891262, 7: 0.54673011323966825, 8: 0.1717679975696059, 9: 0.19271429069285129, 10: 0.031462511202520964, 11: 4.1563444464231249})
    #main({1: 0.38255083329257689, 2: 720.92819210954269, 3: 0.44757236906378917, 4: 6979.2565937495028, 5: 18176.733696356445, 6: 2.7646861964082938, 7: 127027.95319359133, 8: 2.4220402584369252, 9: 1717.5490514101077, 10: 14321.455663758181, 11: 1.4558893578721763})
    