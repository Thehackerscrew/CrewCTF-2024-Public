import random
from typing import Optional

from tqdm import tqdm

from generation.constants import *
from generation.io import write

random.seed(0)

FLAG: bytes = b"crew{h3_n3v3r_4rr1v3d_9c6ddf}"
# FLAG: bytes = b"cr"

TWO_AHEAD_TILES: dict[tuple[tuple[int, int, int], tuple[int, int, int]]: tuple[int, int]] = {
    (NORTH, SOUTH): (WIRE_NS_OFF, WIRE_NS_ON),
    (SOUTH, NORTH): (WIRE_NS_OFF, WIRE_NS_ON),
    (EAST, WEST): (WIRE_EW_OFF, WIRE_EW_ON),
    (WEST, EAST): (WIRE_EW_OFF, WIRE_EW_ON),
    (NORTH, EAST): (CORNER_NE_OFF, CORNER_NE_ON),
    (EAST, NORTH): (CORNER_NE_OFF, CORNER_NE_ON),
    (EAST, SOUTH): (CORNER_ES_OFF, CORNER_ES_ON),
    (SOUTH, EAST): (CORNER_ES_OFF, CORNER_ES_ON),
    (SOUTH, WEST): (CORNER_SW_OFF, CORNER_SW_ON),
    (WEST, SOUTH): (CORNER_SW_OFF, CORNER_SW_ON),
    (WEST, NORTH): (CORNER_WN_OFF, CORNER_WN_ON),
    (NORTH, WEST): (CORNER_WN_OFF, CORNER_WN_ON),
    (NORTH, UP): (VIA_N_OFF, VIA_N_ON),
    (UP, NORTH): (VIA_N_OFF, VIA_N_ON),
    (NORTH, DOWN): (VIA_N_OFF, VIA_N_ON),
    (DOWN, NORTH): (VIA_N_OFF, VIA_N_ON),
    (EAST, UP): (VIA_E_OFF, VIA_E_ON),
    (UP, EAST): (VIA_E_OFF, VIA_E_ON),
    (EAST, DOWN): (VIA_E_OFF, VIA_E_ON),
    (DOWN, EAST): (VIA_E_OFF, VIA_E_ON),
    (SOUTH, UP): (VIA_S_OFF, VIA_S_ON),
    (UP, SOUTH): (VIA_S_OFF, VIA_S_ON),
    (SOUTH, DOWN): (VIA_S_OFF, VIA_S_ON),
    (DOWN, SOUTH): (VIA_S_OFF, VIA_S_ON),
    (WEST, UP): (VIA_W_OFF, VIA_W_ON),
    (UP, WEST): (VIA_W_OFF, VIA_W_ON),
    (WEST, DOWN): (VIA_W_OFF, VIA_W_ON),
    (DOWN, WEST): (VIA_W_OFF, VIA_W_ON),
    (UP, DOWN): (VIA_NONE_OFF, VIA_NONE_ON),
    (DOWN, UP): (VIA_NONE_OFF, VIA_NONE_ON),
}


class Gate:
    pass


class Fork(Gate):
    south: Optional[Gate]
    east: Optional[Gate]
    west: Optional[Gate]

    def __init__(self) -> None:
        self.south = None
        self.east = None
        self.west = None

    @property
    def on(self) -> bool:
        assert self.south is not None

        return self.south.on

    @property
    def tile(self) -> int:
        if self.south.on:
            return FORK_ESW_ON
        else:
            return FORK_ESW_OFF


class And(Gate):
    east: Optional[Gate]
    west: Optional[Gate]
    north: Optional[Gate]

    def __init__(self) -> None:
        self.east = None
        self.west = None
        self.north = None

    @property
    def on(self) -> bool:
        assert self.east is not None
        assert self.west is not None

        return self.east.on and self.west.on

    @property
    def tile(self) -> int:
        match (self.east.on, self.west.on):
            case (False, False):
                return AND_E_OFF_W_OFF
            case (False, True):
                return AND_E_OFF_W_ON
            case (True, False):
                return AND_E_ON_W_OFF
            case (True, True):
                return AND_E_ON_W_ON


class Or(Gate):
    east: Optional[Gate]
    west: Optional[Gate]
    north: Optional[Gate]

    def __init__(self) -> None:
        self.east = None
        self.west = None
        self.north = None

    @property
    def on(self) -> bool:
        assert self.east is not None
        assert self.west is not None

        return self.east.on or self.west.on

    @property
    def tile(self) -> int:
        match (self.east.on, self.west.on):
            case (False, False):
                return OR_E_OFF_W_OFF
            case (False, True):
                return OR_E_OFF_W_ON
            case (True, False):
                return OR_E_ON_W_OFF
            case (True, True):
                return OR_E_ON_W_ON


class Xor(Gate):
    east: Optional[Gate]
    west: Optional[Gate]
    north: Optional[Gate]

    def __init__(self) -> None:
        self.east = None
        self.west = None
        self.north = None

    @property
    def on(self) -> bool:
        assert self.east is not None
        assert self.west is not None

        return self.east.on != self.west.on

    @property
    def tile(self) -> int:
        match (self.east.on, self.west.on):
            case (False, False):
                return XOR_E_OFF_W_OFF
            case (False, True):
                return XOR_E_OFF_W_ON
            case (True, False):
                return XOR_E_ON_W_OFF
            case (True, True):
                return XOR_E_ON_W_ON


class Not(Gate):
    south: Optional[Gate]
    north: Optional[Gate]

    def __init__(self) -> None:
        self.south = None
        self.north = None

    @property
    def on(self) -> bool:
        assert self.south is not None

        return not self.south.on

    @property
    def tile(self) -> int:
        if self.on:
            return NOT_S_OFF
        else:
            return NOT_S_ON


class Switch(Gate):
    on: bool
    north: Optional[Gate]

    def __init__(self, on: bool) -> None:
        self.on = on
        self.north = None

    @property
    def tile(self) -> int:
        if self.on:
            return SWITCH_N_ON
        else:
            return SWITCH_N_OFF


class Light(Gate):
    south: Optional[Gate]

    def __init__(self) -> None:
        self.south = None

    @property
    def on(self) -> bool:
        assert self.south is not None

        return self.south.on

    @property
    def tile(self) -> int:
        if self.on:
            return LIGHT_S_ON
        else:
            return LIGHT_S_OFF


class Tile(Gate):
    tile: int

    def __init__(self, tile: int) -> None:
        self.tile = tile


class Dummy(Gate):
    pass


class Grid:
    forward: dict[tuple[int, int, int], Gate]
    reverse: dict[Gate, tuple[int, int, int]]

    def __init__(self) -> None:
        self.forward = {}
        self.reverse = {}

    def add(self, position: tuple[int, int, int], gate: Gate) -> None:
        assert position not in self.forward

        self.forward[position] = gate
        self.reverse[gate] = position

    def get_gate(self, position: tuple[int, int, int]) -> Gate:
        return self.forward[position]

    def get_position(self, gate: Gate) -> tuple[int, int, int]:
        return self.reverse[gate]


class Positioner:
    layer: int
    positive: bool
    position: int

    def __init__(self) -> None:
        self.layer = 0
        self.positive = True
        self.position = 0

    def next(self) -> tuple[int, int]:
        x = self.position - self.layer
        y = self.layer - abs(x)
        x *= 5
        y *= 5
        if self.positive:
            y += 4
        else:
            y = -y
            y -= 4

        if self.layer * 2 == self.position:
            self.positive = not self.positive
            self.position = 0
            if self.positive:
                self.layer += 1
        else:
            self.position += 1

        return x, y


def vector_add(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def vector_sub(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def vector_manhattan(a: tuple[int, int, int]) -> int:
    return abs(a[0]) + abs(a[1]) + abs(a[2]) * 8


# z meta, not in open path
def a_star(grid: Grid, disallowed_vias: set[tuple[int, int]], from_position: tuple[int, int, int], to_position: tuple[int, int, int]) -> tuple[tuple[int, int, int], ...]:
    open_set = {from_position}
    came_from = {}
    g_score = {from_position: 0}
    h = lambda x: vector_manhattan(vector_sub(to_position, x))
    f_score = {from_position: h(from_position)}

    while len(open_set):
        best_position = None
        best_f_score = 0xffffffffffffffff
        for position in open_set:
            if f_score[position] < best_f_score:
                best_position = position
                best_f_score = f_score[position]

        if best_position == to_position:
            break

        open_set.remove(best_position)

        for vector in (NORTH, EAST, SOUTH, WEST, UP, DOWN):
            next_ = vector_add(best_position, vector)

            if next_ in grid.forward:
                continue

            if next_[:2] in disallowed_vias:
                continue

            if vector == DOWN and next_[:2] != from_position[:2]:
                continue

            if vector == UP and next_[:2] != to_position[:2]:
                continue

            tentative_g_score = g_score[best_position] + 1
            if tentative_g_score < g_score.get(next_, 0xffffffffffffffff):
                came_from[next_] = best_position
                g_score[next_] = tentative_g_score
                f_score[next_] = tentative_g_score + h(next_)
                if next_ not in open_set:
                    open_set.add(next_)

    current = to_position
    path = [to_position]
    while current in came_from:
        current = came_from[current]
        path.append(current)

    return tuple(path[::-1])


def djikstra(grid: Grid, disallowed_vias: set[tuple[int, int]], from_position: tuple[int, int, int], to_position: tuple[int, int, int]) -> tuple[tuple[int, int, int], ...]:
    distances = {from_position: 0}
    paths = {from_position: (from_position,)}
    unvisited = {from_position}

    while True:
        best_distance = 0xffffffffffffffff
        best_position = None
        for position in unvisited:
            if distances[position] < best_distance:
                best_distance = distances[position]
                best_position = position

        if best_position == to_position:
            break

        unvisited.remove(best_position)

        for vector in (NORTH, EAST, SOUTH, WEST, UP, DOWN):
            next_ = vector_add(best_position, vector)
            if next_ in grid.forward:
                continue

            if next_[:2] in disallowed_vias:
                continue

            if vector == DOWN and next_[:2] != from_position[:2]:
                continue

            if vector == UP and next_[:2] != to_position[:2]:
                continue

            if best_distance + 1 < distances.get(next_, 0xffffffffffffffff):
                distances[next_] = best_distance + 1
                paths[next_] = paths[best_position] + (next_,)
                unvisited.add(next_)

    return paths[to_position]


def path_find(grid: Grid, disallowed_vias: set[tuple[int, int]], from_: Gate, to: Gate) -> None:
    if isinstance(from_, And) or isinstance(from_, Or) or isinstance(from_, Xor) or isinstance(from_, Not) or isinstance(from_, Switch) or isinstance(from_, Light):
        from_position = vector_add(grid.get_position(from_), NORTH)
    elif isinstance(from_, Fork):
        if from_.east == to:
            from_position = vector_add(grid.get_position(from_), EAST)
        elif from_.west == to:
            from_position = vector_add(grid.get_position(from_), WEST)
        else:
            assert False
    else:
        assert False

    if isinstance(to, And) or isinstance(to, Or) or isinstance(to, Xor):
        if to.east == from_:
            to_position = vector_add(grid.get_position(to), EAST)
        elif to.west == from_:
            to_position = vector_add(grid.get_position(to), WEST)
        else:
            assert False
    elif isinstance(to, Fork) or isinstance(to, Not) or isinstance(to, Switch) or isinstance(to, Light):
        to_position = vector_add(grid.get_position(to), SOUTH)
    else:
        assert False

    disallowed_vias.remove((from_position[0], from_position[1]))
    disallowed_vias.remove((to_position[0], to_position[1]))

    path = (grid.get_position(from_),) + a_star(grid, disallowed_vias, from_position, to_position) + (grid.get_position(to),)

    for i in range(len(path) - 2):
        a = path[i]
        b = path[i + 1]
        c = path[i + 2]
        d = vector_sub(a, b)
        e = vector_sub(c, b)

        if (d[2] != 0) != (e[2] != 0):
            direction = d[2] + e[2]
            if direction > 0:
                grid.add(vector_add(b, DOWN), Dummy())
            else:
                grid.add(vector_add(b, UP), Dummy())

        tile = TWO_AHEAD_TILES[(d, e)][1 if from_.on else 0]
        grid.add(b, Tile(tile))


def main() -> None:
    bits = []
    for byte in FLAG:
        for bit in f"{byte:08b}":
            bits.append(bit == "1")

    gates = set()

    switches = []
    heads = set()
    for bit in bits:
        switch = Switch(bit)  # Later we're going to have to turn all switches off.
        switches.append(switch)
        heads.add(switch)
        gates.add(switch)

    while len(heads) != 1:
        east = heads.pop()
        if random.randint(0, 3) == 0:  # 1/4 chance to swap
            not_ = Not()
            not_.south = east
            east.north = not_
            gates.add(not_)
            east = not_

        west = heads.pop()
        if random.randint(0, 3) == 0:  # 1/4 chance to swap
            not_ = Not()
            not_.south = west
            west.north = not_
            gates.add(not_)
            west = not_

        if east.on and not west.on:  # Make east=on,west=off to east=off,west=on.
            east, west = west, east

        match east.on, west.on:
            case False, False:
                match random.randint(0,  2):
                    case 0:  # a or b = 0
                        or_ = Or()
                        or_.east = east
                        east.north = or_
                        or_.west = west
                        west.north = or_
                        heads.add(or_)
                        gates.add(or_)
                    case 1:  # (a xor b) or (a and b) = 0
                        east_fork = Fork()
                        east_fork.south = east
                        east.north = east_fork
                        gates.add(east_fork)

                        west_fork = Fork()
                        west_fork.south = west
                        west.north = west_fork
                        gates.add(west_fork)

                        xor = Xor()
                        xor.east = east_fork
                        east_fork.east = xor
                        xor.west = west_fork
                        west_fork.east = xor
                        gates.add(xor)

                        and_ = And()
                        and_.east = east_fork
                        east_fork.west = and_
                        and_.west = west_fork
                        west_fork.west = and_
                        gates.add(and_)

                        or_ = Or()
                        or_.east = xor
                        xor.north = or_
                        or_.west = and_
                        and_.north = or_
                        heads.add(or_)
                        gates.add(or_)
                    case 2:  # (not a) and (not b) = 1
                        east_not = Not()
                        east_not.south = east
                        east.north = east_not
                        gates.add(east_not)

                        west_not = Not()
                        west_not.south = west
                        west.north = west_not
                        gates.add(west_not)

                        and_ = And()
                        and_.east = east_not
                        east_not.north = and_
                        and_.west = west_not
                        west_not.north = and_
                        heads.add(and_)
                        gates.add(and_)
            case False, True:
                match random.randint(0, 2):
                    case 0:  # (a xor b) and a = 1
                        fork = Fork()
                        fork.south = west
                        west.north = fork
                        gates.add(fork)

                        xor = Xor()
                        xor.east = east
                        east.north = xor
                        xor.west = fork
                        fork.east = xor
                        gates.add(xor)

                        and_ = And()
                        and_.east = xor
                        xor.north = and_
                        and_.west = fork
                        fork.west = and_
                        heads.add(and_)
                        gates.add(and_)
                    case 1:  # (not a) and b = 1
                        not_ = Not()
                        not_.south = east
                        east.north = not_
                        gates.add(not_)

                        and_ = And()
                        and_.east = not_
                        not_.north = and_
                        and_.west = west
                        west.north = and_
                        heads.add(and_)
                        gates.add(and_)
                    case 2:  # (not b) or a = 0
                        not_ = Not()
                        not_.south = west
                        west.north = not_
                        gates.add(not_)

                        or_ = Or()
                        or_.east = east
                        east.north = or_
                        or_.west = not_
                        not_.north = or_
                        heads.add(or_)
                        gates.add(or_)
            case True, True:
                match random.randint(0, 1):
                    case 0:  # a and b = 1
                        and_ = And()
                        and_.east = east
                        east.north = and_
                        and_.west = west
                        west.north = and_
                        heads.add(and_)
                        gates.add(and_)
                    case 1:  # (a xor b) xor (a or b) = 1
                        east_fork = Fork()
                        east_fork.south = east
                        east.north = east_fork
                        gates.add(east_fork)

                        west_fork = Fork()
                        west_fork.south = west
                        west.north = west_fork
                        gates.add(west_fork)

                        xor_start = Xor()
                        xor_start.east = east_fork
                        east_fork.east = xor_start
                        xor_start.west = west_fork
                        west_fork.east = xor_start
                        gates.add(xor_start)

                        or_ = Or()
                        or_.east = east_fork
                        east_fork.west = or_
                        or_.west = west_fork
                        west_fork.west = or_
                        gates.add(or_)

                        xor_end = Xor()
                        xor_end.east = xor_start
                        xor_start.north = xor_end
                        xor_end.west = or_
                        or_.north = xor_end
                        heads.add(xor_end)
                        gates.add(xor_end)
                    case 2:  # (not a) or (not b) = 0
                        east_not = Not()
                        east_not.south = east
                        east.north = east_not
                        gates.add(east_not)

                        west_not = Not()
                        west_not.south = west
                        west.north = west_not
                        gates.add(west_not)

                        or_ = And()
                        or_.east = east_not
                        east_not.north = or_
                        or_.west = west_not
                        west_not.north = or_
                        heads.add(or_)
                        gates.add(or_)

    last_head = heads.pop()

    if not last_head.on:
        not_ = Not()
        not_.south = last_head
        last_head.north = not_

        last_head = not_

    light = Light()
    light.south = last_head
    light.south.north = light
    gates.add(light)

    for switch in switches:
        switch.on = False

    grid = Grid()
    disallowed_vias = set()

    grid.add((0, 1, 0), light)
    disallowed_vias.add((0, 0))

    half_len_bits = len(bits) // 2
    for i, switch in enumerate(switches):
        x = i - half_len_bits
        if i >= half_len_bits:
            x += 1
        x *= 2

        grid.add((x, -1, 0), switch)
        disallowed_vias.add((x, 0))

    positioner = Positioner()
    for gate in gates:
        if isinstance(gate, Switch) or isinstance(gate, Light):  # Already positioned.
            continue

        position = positioner.next()
        grid.add((position[0], position[1], random.randint(-(len(gates) // 16 + 1), -1)), gate)

        if isinstance(gate, And) or isinstance(gate, Or) or isinstance(gate, Xor) or isinstance(gate, Not):
            disallowed_vias.add((position[0], position[1] + 1))
        elif isinstance(gate, Fork):
            disallowed_vias.add((position[0] - 1, position[1]))
            disallowed_vias.add((position[0] + 1, position[1]))
        else:
            assert False

        if isinstance(gate, And) or isinstance(gate, Or) or isinstance(gate, Xor):
            disallowed_vias.add((position[0] - 1, position[1]))
            disallowed_vias.add((position[0] + 1, position[1]))
        elif isinstance(gate, Fork) or isinstance(gate, Not):
            disallowed_vias.add((position[0], position[1] - 1))
        else:
            assert False

    for gate in tqdm(gates):
        if isinstance(gate, Light):  # No outs.
            continue

        if isinstance(gate, Switch) or isinstance(gate, And) or isinstance(gate, Or) or isinstance(gate, Xor) or isinstance(gate, Not):
            path_find(grid, disallowed_vias, gate, gate.north)
        elif isinstance(gate, Fork):
            path_find(grid, disallowed_vias, gate, gate.east)
            path_find(grid, disallowed_vias, gate, gate.west)

    tile_grid = {}
    for position, gate in grid.forward.items():
        if isinstance(gate, Dummy):
            continue

        tile_grid[position] = gate.tile

    with (LEVELS_PATH / "3").open("wb") as f:
        write(f, tile_grid)


if __name__ == "__main__":
    main()
