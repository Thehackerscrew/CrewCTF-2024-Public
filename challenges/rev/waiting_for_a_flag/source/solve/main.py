import struct
from abc import ABC, abstractmethod
from typing import BinaryIO

import z3

from solve.constants import *


class Gate(ABC):
    ins: list["Gate"]

    def __init__(self):
        self.ins = []

    @property
    @abstractmethod
    def on(self):
        pass


class And(Gate):
    @property
    def on(self):
        assert len(self.ins) == 2
        return z3.And(self.ins[0].on, self.ins[1].on)


class Or(Gate):
    @property
    def on(self):
        assert len(self.ins) == 2
        return z3.Or(self.ins[0].on, self.ins[1].on)


class Xor(Gate):
    @property
    def on(self):
        assert len(self.ins) == 2
        return z3.Xor(self.ins[0].on, self.ins[1].on)


class Not(Gate):
    @property
    def on(self):
        assert len(self.ins) == 1
        return z3.Not(self.ins[0].on)


class Switch(Gate):
    def __init__(self, name):
        super().__init__()
        self.value = z3.Bool(name)

    @property
    def on(self):
        return self.value


class Light(Gate):
    @property
    def on(self):
        assert len(self.ins) == 1
        return self.ins[0].on


def read(buffer: BinaryIO) -> dict[tuple[int, int, int], int]:
    grid = {}
    while True:
        item = buffer.read(13)
        if len(item) != 13:
            break

        x, y, z, tile = struct.unpack("<lllB", item)
        grid[(x, y, z)] = tile

    return grid


def vector_add(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def vector_sub(a: tuple[int, int, int], b: tuple[int, int, int]) -> tuple[int, int, int]:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]

def main() -> None:
    with (LEVELS_PATH / "3").open("rb") as f:
        grid = read(f)

    switches = []
    for position, tile in grid.items():
        if tile in (SWITCH_N_OFF, SWITCH_N_ON):
            switches.append(position)

    switches.sort()

    stack = []
    bits = []
    for i, position in enumerate(switches):
        switch = Switch(f"s{i}")
        stack.append((position, switch, None))
        bits.append(switch.on)

    lookup = {}

    while len(stack):
        position, gate, direction = stack.pop()

        if position not in grid:
            assert direction in (UP, DOWN)
            continue

        if grid[position] in (FORK_ESW_OFF, FORK_ESW_ON):
            assert direction == SOUTH
            stack.append((vector_add(position, EAST), gate, WEST))
            stack.append((vector_add(position, WEST), gate, EAST))
        elif grid[position] in (AND_E_OFF_W_OFF, AND_E_OFF_W_ON, AND_E_ON_W_OFF, AND_E_ON_W_ON):
            assert direction in (EAST, WEST)
            new_gate = lookup.get(position, And())
            lookup[position] = new_gate
            assert isinstance(new_gate, And)
            new_gate.ins.append(gate)
            if len(new_gate.ins) == 2:
                stack.append((vector_add(position, NORTH), new_gate, SOUTH))
        elif grid[position] in (OR_E_OFF_W_OFF, OR_E_OFF_W_ON, OR_E_ON_W_OFF, OR_E_ON_W_ON):
            assert direction in (EAST, WEST)
            new_gate = lookup.get(position, Or())
            lookup[position] = new_gate
            assert isinstance(new_gate, Or)
            new_gate.ins.append(gate)
            if len(new_gate.ins) == 2:
                stack.append((vector_add(position, NORTH), new_gate, SOUTH))
        elif grid[position] in (XOR_E_OFF_W_OFF, XOR_E_OFF_W_ON, XOR_E_ON_W_OFF, XOR_E_ON_W_ON):
            assert direction in (EAST, WEST)
            new_gate = lookup.get(position, Xor())
            lookup[position] = new_gate
            assert isinstance(new_gate, Xor)
            new_gate.ins.append(gate)
            if len(new_gate.ins) == 2:
                stack.append((vector_add(position, NORTH), new_gate, SOUTH))
        elif grid[position] in (NOT_S_OFF, NOT_S_ON):
            assert direction == SOUTH
            new_gate = lookup.get(position, Not())
            lookup[position] = new_gate
            assert isinstance(new_gate, Not)
            new_gate.ins.append(gate)
            stack.append((vector_add(position, NORTH), new_gate, SOUTH))
        elif grid[position] in (SWITCH_N_OFF, SWITCH_N_ON):
            stack.append((vector_add(position, NORTH), gate, SOUTH))
        elif grid[position] in (LIGHT_S_OFF, LIGHT_S_ON):
            assert direction == SOUTH
            new_gate = lookup.get(position, Light())
            lookup[position] = new_gate
            new_gate.ins.append(gate)
            assert isinstance(new_gate, Light)
        else:
            for m in MOVEMENTS[(direction, grid[position])]:
                stack.append((vector_add(position, m), gate, vector_sub((0, 0, 0), m)))

    equation = None
    for gate in lookup.values():
        if isinstance(gate, Light):
            equation = gate.on

    s = z3.Solver()
    s.add(equation)
    print(s.check())

    m = s.model()

    # https://gchq.github.io/CyberChef/#recipe=Find_/_Replace(%7B'option':'Regex','string':'True'%7D,'1',true,false,true,false)Find_/_Replace(%7B'option':'Regex','string':'False'%7D,'0',true,false,true,false)From_Binary('Space',8)
    for bit in bits:
        print(m.evaluate(bit))


if __name__ == "__main__":
    main()
