import json
import pprint

import taj


pp = pprint.PrettyPrinter(indent=4)


if __name__ == '__main__':

    worker_classes = [taj.Lumberjack, taj.Panner, taj.Miner, taj.Tanker]
    resource_classes = [taj.Water, taj.Stone, taj.Gold, taj.Wood]

    board = taj.Board(500)

    def add_clan(name):
        clan = taj.Clan(name)
        board.add(clan)

        for x in xrange(4):
            p = board.random_position()
            castle = taj.Castle(str(x), p)
            clan.castles.append(castle)

            for x in xrange(4):
                for worker_class in worker_classes:
                    worker = worker_class(clan, castle.position.copy(), board)
                    clan.workers.append(worker)


    add_clan('blue')
    add_clan('red')


    for x in xrange(50):
        for resource_class in resource_classes:
            p = board.random_position()
            resource = resource_class(100, p, board)
            board.add(resource)


    frames = []

    for x in xrange(500):
        board.tick()
        frames.append(board.frame())

    #pp.pprint(frames)

    with open('frames.json', 'w') as fh:
        s = json.dumps(frames)
        fh.write('var frames = {};'.format(s))
