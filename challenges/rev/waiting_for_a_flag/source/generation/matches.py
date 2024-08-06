opposites = {
    "N": "S",
    "E": "W",
    "S": "N",
    "W": "E",
    "U": "D",
    "D": "U",
}

longs = {
    "N": "NORTH",
    "E": "EAST",
    "S": "SOUTH",
    "W": "WEST",
    "U": "UP",
    "D": "DOWN",
}

bools = {
    True: "true",
    False: "false",
}

oo = {
    True: "ON",
    False: "OFF",
}

for d in ("NS", "EW"):
    for x in (True, False):
        for f in d:
            print(f"        [WIRE_{d}_{oo[not x]}, {longs[f]}, {bools[x]}]:")
            print(f"            set_tile(destination_coordinate, WIRE_{d}_{oo[x]})")
            print(f"            propogate(destination_coordinate, {longs[f]}, {bools[x]})")

for d in ("NE", "ES", "SW", "WN"):
    for x in (True, False):
        for i in (0, 1):
            print(f"        [CORNER_{d}_{oo[not x]}, {longs[opposites[d[i]]]}, {bools[x]}]:")
            print(f"            set_tile(destination_coordinate, CORNER_{d}_{oo[x]})")
            print(f"            propogate(destination_coordinate, {longs[d[1-i]]}, {bools[x]})")

for d in ("NES", "ESW", "SWN", "WNE"):
    for x in (True, False):
        for i in (0, 1, 2):
            print(f"        [FORK_{d}_{oo[not x]}, {longs[opposites[d[i]]]}, {bools[x]}]:")
            print(f"            set_tile(destination_coordinate, FORK_{d}_{oo[x]})")
            print(f"            propogate(destination_coordinate, {longs[d[(i + 1) % 3]]}, {bools[x]})")
            print(f"            propogate(destination_coordinate, {longs[d[(i + 2) % 3]]}, {bools[x]})")

for d in ("NESW",):
    for x in (True, False):
        for i in (0, 1, 2, 3):
            print(f"        [ALL_{oo[not x]}, {longs[opposites[d[i]]]}, {bools[x]}]:")
            print(f"            set_tile(destination_coordinate, ALL_{oo[x]})")
            print(f"            propogate(destination_coordinate, {longs[d[(i + 1) % 4]]}, {bools[x]})")
            print(f"            propogate(destination_coordinate, {longs[d[(i + 2) % 4]]}, {bools[x]})")
            print(f"            propogate(destination_coordinate, {longs[d[(i + 3) % 4]]}, {bools[x]})")

for d in ("NUD", "EUD", "SUD", "WUD"):
    for x in (True, False):
        for i in (0, 1, 2):
            print(f"        [VIA_{d[0]}_{oo[not x]}, {longs[opposites[d[i]]]}, {bools[x]}]:")
            print(f"            set_tile(destination_coordinate, VIA_{d[0]}_{oo[x]})")
            print(f"            propogate(destination_coordinate, {longs[d[(i + 1) % 3]]}, {bools[x]})")
            print(f"            propogate(destination_coordinate, {longs[d[(i + 2) % 3]]}, {bools[x]})")

for g, o in (("AND", lambda a, b: a and b), ("OR", lambda a, b: a or b), ("XOR", lambda a, b: a != b)):
    for e in (True, False):
        for w in (True, False):
            print(f"        [{g}_E_{oo[e]}_W_{oo[w]}, EAST, {bools[not w]}]:")
            print(f"            set_tile(destination_coordinate, {g}_E_{oo[e]}_W_{oo[not w]})")
            if o(e, w) != o(e, not w):
                print(f"            propogate(destination_coordinate, NORTH, {bools[o(e, not w)]})")

            print(f"        [{g}_E_{oo[e]}_W_{oo[w]}, WEST, {bools[not e]}]:")
            print(f"            set_tile(destination_coordinate, {g}_E_{oo[not e]}_W_{oo[w]})")
            if o(e, w) != o(not e, w):
                print(f"            propogate(destination_coordinate, NORTH, {bools[o(not e, w)]})")

for x in (True, False):
    print(f"        [NOT_S_{oo[not x]}, NORTH, {bools[x]}]:")
    print(f"            set_tile(destination_coordinate, NOT_S_{oo[x]})")
    print(f"            propogate(destination_coordinate, NORTH, {bools[not x]})")

for x in (True, False):
    print(f"        [LIGHT_S_{oo[not x]}, NORTH, {bools[x]}]:")
    print(f"            set_tile(destination_coordinate, LIGHT_S_{oo[x]})")
    print(f"            change_light(destination_coordinate, {bools[x]})")

for d in ("UD",):
    for x in (True, False):
        for i in (0, 1):
            print(f"        [VIA_NONE_{oo[not x]}, {longs[opposites[d[i]]]}, {bools[x]}]:")
            print(f"            set_tile(destination_coordinate, VIA_NONE_{oo[x]})")
            print(f"            propogate(destination_coordinate, {longs[d[(i + 1) % 2]]}, {bools[x]})")
