from pathlib import Path
import pickle
import re

from instructions import *

nodes = pickle.loads((Path(__file__).parent / "nodes.pickle").read_bytes())
keys = (Path(__file__).parent / "keys.data").read_bytes()

INITIAL_NODE = 0x422700
FINAL_NODE = 0x40a490

nodes[INITIAL_NODE]["path"] = (INITIAL_NODE,)

while True:
    best_distance = 0xffffffffffffffff
    best_node = None
    for node in nodes.keys():
        if not nodes[node]["visited"] and nodes[node]["distance"] < best_distance:
            best_distance = nodes[node]["distance"]
            best_node = node

    if best_node == FINAL_NODE:
        break

    nodes[best_node]["visited"] = 1

    for connection in nodes[best_node]["connections"]:
        if nodes[best_node]["distance"] + connection["distance"] < nodes[connection["node"]]["distance"]:
            nodes[connection["node"]]["distance"] = nodes[best_node]["distance"] + connection["distance"]
            nodes[connection["node"]]["path"] = nodes[best_node]["path"] + (connection["node"],)


def get_instruction(assembly: str) -> Instruction:
    match = re.match(r"(?P<instruction>[a-z]+) +xmm0, xmmword \[r15\+0x(?P<offset>[0-9a-f]+)\]", assembly)

    instruction_class = {
        "paddb": AddbInstruction,
        "paddw": AddwInstruction,
        "paddd": AdddInstruction,
        "paddq": AddqInstruction,
        "pshufb": ShufbInstruction,
        "psubb": SubbInstruction,
        "psubw": SubwInstruction,
        "psubd": SubdInstruction,
        "psubq": SubqInstruction,
        "pxor": XorInstruction,
    }[match.group("instruction")]

    offset = int(match.group("offset"), 16)

    return instruction_class(offset, keys[offset:offset+0x10])


COMPARISON = bytes.fromhex("3483db49e20ca85f8a253766f860d0df")

flag = COMPARISON
for node in nodes[FINAL_NODE]["path"][::-1]:
    instruction = get_instruction(nodes[node]["instruction"])
    flag = instruction.reverse(flag)

print(flag.decode())
