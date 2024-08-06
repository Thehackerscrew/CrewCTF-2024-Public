from pathlib import Path

LEVELS_PATH: Path = Path(__file__).parent.parent / "waiting_for_a_flag" / "levels"

WIRE_NS_OFF: int = 0
WIRE_EW_OFF: int = 1
WIRE_NS_ON: int = 2
WIRE_EW_ON: int = 3
CORNER_NE_OFF: int = 4
CORNER_ES_OFF: int = 5
CORNER_SW_OFF: int = 6
CORNER_WN_OFF: int = 7
CORNER_NE_ON: int = 8
CORNER_ES_ON: int = 9
CORNER_SW_ON: int = 10
CORNER_WN_ON: int = 11
FORK_NES_OFF: int = 12
FORK_ESW_OFF: int = 13
FORK_SWN_OFF: int = 14
FORK_WNE_OFF: int = 15
FORK_NES_ON: int = 16
FORK_ESW_ON: int = 17
FORK_SWN_ON: int = 18
FORK_WNE_ON: int = 19
ALL_OFF: int = 20
ALL_ON: int = 21
VIA_N_OFF: int = 22
VIA_E_OFF: int = 23
VIA_S_OFF: int = 24
VIA_W_OFF: int = 25
VIA_N_ON: int = 26
VIA_E_ON: int = 27
VIA_S_ON: int = 28
VIA_W_ON: int = 29
AND_E_OFF_W_OFF: int = 30
AND_E_ON_W_OFF: int = 31
AND_E_OFF_W_ON: int = 32
AND_E_ON_W_ON: int = 33
OR_E_OFF_W_OFF: int = 34
OR_E_ON_W_OFF: int = 35
OR_E_OFF_W_ON: int = 36
OR_E_ON_W_ON: int = 37
XOR_E_OFF_W_OFF: int = 38
XOR_E_ON_W_OFF: int = 39
XOR_E_OFF_W_ON: int = 40
XOR_E_ON_W_ON: int = 41
NOT_S_OFF: int = 42
NOT_S_ON: int = 43
SWITCH_N_OFF: int = 44
SWITCH_N_ON: int = 45
LIGHT_S_OFF: int = 46
LIGHT_S_ON: int = 47
VIA_NONE_OFF: int = 48
VIA_NONE_ON: int = 49

NORTH: tuple[int, int, int] = (0, 1, 0)
SOUTH: tuple[int, int, int] = (0, -1, 0)
EAST: tuple[int, int, int] = (1, 0, 0)
WEST: tuple[int, int, int] = (-1, 0, 0)
UP: tuple[int, int, int] = (0, 0, 1)
DOWN: tuple[int, int, int] = (0, 0, -1)

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

MOVEMENTS: dict[tuple[tuple[int, int, int], int]: list[tuple[int, int, int]]] = {}


def setup_movements():
    for (a, b), (c, d) in TWO_AHEAD_TILES.items():
        x = MOVEMENTS.get((a, c), [])
        MOVEMENTS[(a, c)] = x
        x.append(b)

        x = MOVEMENTS.get((a, d), [])
        MOVEMENTS[(a, d)] = x
        x.append(b)


setup_movements()
