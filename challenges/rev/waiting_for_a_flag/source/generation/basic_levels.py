from generation.constants import *
from generation.io import write


def write_basic_levels() -> None:
    with (LEVELS_PATH / "0").open("wb") as f:
        write(f, {
            (0, -1, 0): SWITCH_N_OFF,
            (0, 0, 0): WIRE_NS_OFF,
            (0, 1, 0): LIGHT_S_OFF,
        })

    with (LEVELS_PATH / "1").open("wb") as f:
        write(f, {
            (-6, -1, 0): SWITCH_N_OFF,
            (-4, -1, 0): SWITCH_N_OFF,
            (-2, -1, 0): SWITCH_N_OFF,
            (0, -1, 0): SWITCH_N_OFF,
            (2, -1, 0): SWITCH_N_ON,
            (4, -1, 0): SWITCH_N_ON,
            (6, -1, 0): SWITCH_N_ON,
            (-6, 0, 0): CORNER_ES_OFF,
            (-4, 0, 0): CORNER_SW_OFF,
            (-2, 0, 0): CORNER_ES_OFF,
            (0, 0, 0): CORNER_SW_OFF,
            (2, 0, 0): CORNER_ES_ON,
            (4, 0, 0): CORNER_SW_ON,
            (-5, 0, 0): AND_E_OFF_W_OFF,
            (-1, 0, 0): OR_E_OFF_W_OFF,
            (3, 0, 0): XOR_E_ON_W_ON,
            (6, 0, 0): NOT_S_ON,
            (-5, 1, 0): LIGHT_S_OFF,
            (-1, 1, 0): LIGHT_S_OFF,
            (3, 1, 0): LIGHT_S_OFF,
            (6, 1, 0): LIGHT_S_OFF,
        })

        with (LEVELS_PATH / "2").open("wb") as f:
            write(f, {
                (-1, 0, 0): SWITCH_N_OFF,
                (1, 0, 0): SWITCH_N_OFF,
                (-1, 1, 0): VIA_S_OFF,
                (1, 1, 0): VIA_S_OFF,
                (0, -2, 0): VIA_N_OFF,
                (0, -1, 0): LIGHT_S_OFF,
                (-1, 1, -1): VIA_N_OFF,
                (1, 1, -1): VIA_N_OFF,
                (-1, 2, -1): CORNER_ES_OFF,
                (1, 2, -1): CORNER_SW_OFF,
                (0, 2, -1): AND_E_OFF_W_OFF,
                (0, 3, -1): CORNER_ES_OFF,
                (1, 3, -1): WIRE_EW_OFF,
                (2, 3, -1): CORNER_SW_OFF,
                (2, 2, -1): WIRE_NS_OFF,
                (2, 1, -1): WIRE_NS_OFF,
                (2, 0, -1): CORNER_WN_OFF,
                (1, 0, -1): WIRE_EW_OFF,
                (0, 0, -1): CORNER_ES_OFF,
                (0, -1, -1): WIRE_NS_OFF,
                (0, -2, -1): VIA_N_OFF,
            })


def f(x, y):
    return (x + y) // 2, x - y


if __name__ == "__main__":
    write_basic_levels()
