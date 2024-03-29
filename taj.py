from collections import Counter, defaultdict, namedtuple
import math
import random

from euclid import Vector2


class Position(Vector2):
    def frame(self):
        return {
            'x': self.x,
            'y': self.y,
        }


class Board(object):

    def __init__(self, size):
        self.size = size
        self._objects = []

    def add(self, obj):
        self._objects.append(obj)

    def remove(self, obj):
        self._objects.remove(obj)

    def objects_by_type(self, type_):
        objs = []
        for obj in self._objects:
            if isinstance(obj, type_):
                objs.append(obj)
        return objs

    def random_position(self):
        x = random.randint(0, self.size)
        y = random.randint(0, self.size)
        return Position(x, y)

    def distance(self, a, b):
        a = a.position
        b = b.position
        return math.hypot(b.x - a.x, b.y - a.y)

    def tick(self):
        for obj in self._objects:
            if hasattr(obj, 'tick'):
                obj.tick()

    def frame(self):
        d = {
            'size': self.size,
            'objects': [],
        }
        for obj in self._objects:
            d['objects'].append(obj.frame())
        return d


class Resource(object):
    # TODO block instantiation?

    def __init__(self, amount, position, board):
        self.remaining = amount
        self.position = position
        self.board = board

    def collect(self, amount):
        # TODO coefficient of consumption
        if amount > self.remaining:
            r = self.remaining
            self.remaining = 0
            self.board.remove(self)
            return r
        else:
            self.remaining -= amount
            return amount

    def frame(self):
        return {
            'type': self.__class__.__name__,
            'position': self.position.frame(),
            'remaining': self.remaining,
        }


class Wood(Resource): pass

class Water(Resource): pass

class Gold(Resource): pass

class Stone(Resource): pass


class Castle(object):
    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.defense = 10
        self.resources = Counter()

    def tick(self): pass

    def frame(self):
        return {
            'type': self.__class__.__name__,
            'name': self.name,
            'position': self.position.frame(),
            'defense': self.defense,
            'resources': {k.__class__.__name__: c for k, c in self.resources.items()},
        }


class Clan(object):
    def __init__(self, name):
        self.name = name
        # TODO replace with "children" so that all scene graph nodes are consistent
        #      which will make frame and tick easier
        self.castles = []
        self.workers = []

    def tick(self):
        for obj in self.castles + self.workers:
            obj.tick()

    def frame(self):
        return {
            'type': self.__class__.__name__,
            'name': self.name,
            'castles': [castle.frame() for castle in self.castles],
            'workers': [worker.frame() for worker in self.workers],
        }


class Peon(object):
    def __init__(self, clan, position, board):
        self.clan = clan
        self.position = position
        self.board = board
        self.health = 10
        self.movement_speed = 1

    def nearest_friendly_castle(self):
        if self.clan.castles:
            key = lambda castle: self.board.distance(self, castle)
            return sorted(self.clan.castles, key=key)[0]

    def move_towards(self, target):
        direction = target.position - self.position
        self.position += direction.normalized() * self.movement_speed

    def frame(self):
        return {
            'type': self.__class__.__name__,
            'position': self.position.frame(),
            'health': self.health,
            'movement_speed': self.movement_speed,
        }


class Worker(Peon):
    # TODO block instantiation?

    def __init__(self, clan, position, board):
        super(Worker, self).__init__(clan, position, board)

        self.collection_speed = 1
        self.capacity = 10
        self.collected = 0
        self.collecting = True

    def frame(self):
        d = super(Worker, self).frame()
        d.update({
            'collection_speed': self.collection_speed,
            'capacity': self.capacity,
            'collected': self.collected,
            'collecting': self.collecting,
        })
        return d

    def unload(self, castle):
        castle.resources[self.resource_type] += self.collected
        self.collecting = True
        self.collected = 0

    def collect(self, target):
        self.collected += target.collect(self.collection_speed)
        self.collected = min(self.capacity, self.collected)

        if self.collected == self.capacity:
            self.collecting = False

    def targets(self):
        return self.board.objects_by_type(self.resource_type)

    def nearest_target(self):
        targets = self.targets()
        if targets:
            key = lambda target: self.board.distance(self, target)
            return sorted(targets, key=key)[0]
        
    def tick(self):
        # TODO watch out for when a clan can't possibly get more castles
        #      and kill the workers?
        #      could model this as "worker needs food to survive,
        #      so if it hasn't returned
        #      to the castle in X days, it dies"
        #      possibly they will defect to another clan?

        if self.collecting:
            target = self.nearest_target()
            if target:
                if self.board.distance(self, target) < 1:
                    self.collect(target)
                else:
                    self.move_towards(target)

        else:
            castle = self.nearest_friendly_castle()

            if castle:
                if self.board.distance(self, castle) < 1:
                    self.unload(castle)
                else:
                    self.move_towards(castle)


class Lumberjack(Worker):
    resource_type = Wood


class Panner(Worker):
    resource_type = Stone


class Miner(Worker):
    resource_type = Stone


class Tanker(Worker):
    resource_type = Water


# TODO...

class Knight(object):
    def __init__(self, clan):
        self.clan = clan
        self.health = 10
        self.damage = 1

    def tick(self):
        # TODO be able to battle
        if battling:
            pass
        else:
            castle = self.board.nearest_enemy_castle()
            self.move_towards(castle)


class Solider(object):
    def __init__(self, clan):
        self.clan = clan
        self.health = 10
        self.damage = 1

    def tick(self):
        if battling:
            # TODO be able to battle
            pass
        else:
            enemy_peon = self.board.enemies.within(allowed_distance).one()
            if enemy_peon:
                self.move_towards(enemy_peon)

            castle = self.board.nearest_enemy_castle()
            self.move_towards(castle)
