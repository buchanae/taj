import taj


if __name__ == '__main__':

    worker_classes = [taj.Lumberjack, taj.Panner, taj.Miner, taj.Tanker]
    resource_classes = [taj.Water, taj.Stone, taj.Gold, taj.Wood]

    board = taj.Board(100)
    tickables = []

    def make_clan(name):
        clan = taj.Clan(name)

        for x in xrange(4):
            p = board.random_position()
            castle = taj.Castle(p)
            clan.castles.append(castle)

            for x in xrange(4):
                for worker_class in worker_classes:
                    p = board.random_position()
                    worker = worker_class(clan, p, board)
                    tickables.append(worker)
        return clan


    blue = make_clan('blue')
    red = make_clan('red')

    for x in xrange(50):
        for resource_class in resource_classes:
            p = board.random_position()
            resource = resource_class(100, p, board)
            board.add(resource)

    follow = tickables[0]

    for x in xrange(1000):
        for castle in blue.castles:
            print castle.resources

        for t in tickables:
            t.tick()

            if t is follow:
                print t.position
