import random
from pathlib import Path
from typing import Type
import struct
from uuid import UUID, uuid4


FLAG: bytes = b"crew{a6b4291e38}"
DIRECTORY: Path = Path(__file__).parent


def pack2(data: list[int]) -> bytes:
    return struct.pack("<HHHHHHHH", *data)


def unpack2(data: bytes) -> tuple[int, ...]:
    return struct.unpack("<HHHHHHHH", data)


def pack4(data: list[int]) -> bytes:
    return struct.pack("<LLLL", *data)


def unpack4(data: bytes) -> tuple[int, ...]:
    return struct.unpack("<LLLL", data)


def pack8(data: list[int]) -> bytes:
    return struct.pack("<QQ", *data)


def unpack8(data: bytes) -> tuple[int, ...]:
    return struct.unpack("<QQ", data)


class Instruction:
    offset: int
    key: bytes

    def __init__(self, offset: int, key: bytes) -> None:
        self.offset = offset
        self.key = key

    @staticmethod
    def gen_key() -> bytes:
        return random.randbytes(16)

    def forward(self, value: bytes) -> bytes:
        pass

    def reverse(self, value: bytes) -> bytes:
        pass

    def assembly(self) -> str:
        pass


class AddbInstruction(Instruction):  # PADDB
    def forward(self, value: bytes) -> bytes:
        return bytes((a + b) & 0xff for a, b in zip(value, self.key))

    def reverse(self, value: bytes) -> bytes:
        return bytes((a - b) & 0xff for a, b in zip(value, self.key))

    def assembly(self) -> str:
        return f"paddb xmm0, oword [r15 + {self.offset} * 16]"


class AddwInstruction(Instruction):  # PADDW
    def forward(self, value: bytes) -> bytes:
        return pack2([(a + b) & 0xffff for a, b in zip(unpack2(value), unpack2(self.key))])

    def reverse(self, value: bytes) -> bytes:
        return pack2([(a - b) & 0xffff for a, b in zip(unpack2(value), unpack2(self.key))])

    def assembly(self) -> str:
        return f"paddw xmm0, oword [r15 + {self.offset} * 16]"


class AdddInstruction(Instruction):  # PADDD
    def forward(self, value: bytes) -> bytes:
        return pack4([(a + b) & 0xffffffff for a, b in zip(unpack4(value), unpack4(self.key))])

    def reverse(self, value: bytes) -> bytes:
        return pack4([(a - b) & 0xffffffff for a, b in zip(unpack4(value), unpack4(self.key))])

    def assembly(self) -> str:
        return f"paddd xmm0, oword [r15 + {self.offset} * 16]"


class AddqInstruction(Instruction):  # PADDQ
    def forward(self, value: bytes) -> bytes:
        return pack8([(a + b) & 0xffffffffffffffff for a, b in zip(unpack8(value), unpack8(self.key))])

    def reverse(self, value: bytes) -> bytes:
        return pack8([(a - b) & 0xffffffffffffffff for a, b in zip(unpack8(value), unpack8(self.key))])

    def assembly(self) -> str:
        return f"paddq xmm0, oword [r15 + {self.offset} * 16]"


class ShufbInstruction(Instruction):  # PSHUFB
    @staticmethod
    def gen_key() -> bytes:
        result = list(range(16))
        random.shuffle(result)
        return bytes(result)

    def forward(self, value: bytes) -> bytes:
        return bytes(value[i] for i in self.key)

    def reverse(self, value: bytes) -> bytes:
        result = [None] * 16
        for k, v in zip(self.key, value):
            result[k] = v
        return bytes(result)

    def assembly(self) -> str:
        return f"pshufb xmm0, oword [r15 + {self.offset} * 16]"


class SubbInstruction(Instruction):  # PSUBB
    def forward(self, value: bytes) -> bytes:
        return bytes((a - b) & 0xff for a, b in zip(value, self.key))

    def reverse(self, value: bytes) -> bytes:
        return bytes((a + b) & 0xff for a, b in zip(value, self.key))

    def assembly(self) -> str:
        return f"psubb xmm0, oword [r15 + {self.offset} * 16]"


class SubwInstruction(Instruction):  # PSUBW
    def forward(self, value: bytes) -> bytes:
        return pack2([(a - b) & 0xffff for a, b in zip(unpack2(value), unpack2(self.key))])

    def reverse(self, value: bytes) -> bytes:
        return pack2([(a + b) & 0xffff for a, b in zip(unpack2(value), unpack2(self.key))])

    def assembly(self) -> str:
        return f"psubw xmm0, oword [r15 + {self.offset} * 16]"


class SubdInstruction(Instruction):  # PSUBD
    def forward(self, value: bytes) -> bytes:
        return pack4([(a - b) & 0xffffffff for a, b in zip(unpack4(value), unpack4(self.key))])

    def reverse(self, value: bytes) -> bytes:
        return pack4([(a + b) & 0xffffffff for a, b in zip(unpack4(value), unpack4(self.key))])

    def assembly(self) -> str:
        return f"psubd xmm0, oword [r15 + {self.offset} * 16]"


class SubqInstruction(Instruction):  # PSUBQ
    def forward(self, value: bytes) -> bytes:
        return pack8([(a - b) & 0xffffffffffffffff for a, b in zip(unpack8(value), unpack8(self.key))])

    def reverse(self, value: bytes) -> bytes:
        return pack8([(a + b) & 0xffffffffffffffff for a, b in zip(unpack8(value), unpack8(self.key))])

    def assembly(self) -> str:
        return f"psubq xmm0, oword [r15 + {self.offset} * 16]"


class XorInstruction(Instruction):  # PXOR
    def forward(self, value: bytes) -> bytes:
        return bytes(a ^ b for a, b in zip(value, self.key))

    def reverse(self, value: bytes) -> bytes:
        return bytes(a ^ b for a, b in zip(value, self.key))

    def assembly(self) -> str:
        return f"pxor xmm0, oword [r15 + {self.offset} * 16]"


class InstructionGenerator:
    INSTRUCTIONS: tuple[Type[Instruction], ...] = (
        AddbInstruction,
        AddwInstruction,
        AdddInstruction,
        AddqInstruction,
        ShufbInstruction,
        SubbInstruction,
        SubwInstruction,
        SubdInstruction,
        SubqInstruction,
        XorInstruction,
    )

    memory: list[bytes]

    def __init__(self) -> None:
        self.memory = []

    def new_instruction(self) -> Instruction:
        instruction_class = random.choice(InstructionGenerator.INSTRUCTIONS)
        key = instruction_class.gen_key()
        instruction = instruction_class(len(self.memory), key)
        self.memory.append(key)
        return instruction


class Node:
    instruction: Instruction
    connections: list[tuple["Node", int]]
    distance: int
    path: tuple["Node", ...]
    uuid: UUID
    visited: bool

    def __init__(self, instruction: Instruction) -> None:
        self.instruction = instruction
        self.connections = []
        self.distance = 0xffffffffffffffff
        self.path = tuple()
        self.uuid = uuid4()
        self.visited = False


def djikstra(nodes: list[Node], start: Node, end: Node) -> None:
    start.distance = 0
    start.path = (start,)

    while True:
        best_distance = 0xffffffffffffffff
        best_node = None
        for node in nodes:
            if not node.visited and node.distance < best_distance:
                best_distance = node.distance
                best_node = node

        if best_node == end:
            return

        best_node.visited = True

        for node, distance in best_node.connections:
            if best_node.distance + distance < node.distance:
                node.distance = best_node.distance + distance
                node.path = best_node.path + (node,)


def main() -> None:
    random.seed(0)

    ig = InstructionGenerator()

    nodes = []
    for _ in range(1024):
        nodes.append(Node(ig.new_instruction()))

    random.shuffle(nodes)

    for index, node in enumerate(nodes):
        for _ in range(random.randint(1, 8)):
            node.connections.append((random.choice(nodes[max(index - 32, 0):min(index + 32, len(nodes))]), random.randint(1, 255)))

    start = nodes[0]
    end = nodes[-1]

    random.shuffle(nodes)

    djikstra(nodes, start, end)

    print(end.distance, len(end.path))

    unseen = set(InstructionGenerator.INSTRUCTIONS)
    for node in end.path:
        unseen.discard(type(node.instruction))

    assert len(unseen) == 0

    forward = FLAG
    for node in end.path:
        forward = node.instruction.forward(forward)
        print(forward)

    print(forward)

    reverse = forward
    for node in end.path[::-1]:
        reverse = node.instruction.reverse(reverse)

    assert FLAG == reverse

    print(reverse)

    text = []
    for node in nodes:
        text.append(f"instruction_{node.uuid.hex}:\n    {node.instruction.assembly()}\n")

    random.shuffle(text)

    (DIRECTORY / "text.asm").write_text("\n".join(text))

    data = []
    for node in nodes:
        data_ = []
        if node == start:
            data_.append("node_start:\n")
        elif node == end:
            data_.append("node_end:\n")

        data_.append(f"node_{node.uuid.hex}:\n")

        # Distance
        if node == start:
            data_.append("    dq 0\n")
        else:
            data_.append("    dq 0xffffffffffffffff\n")

        # Visited
        data_.append("    dq 0\n")

        # Instruction
        data_.append(f"    dq instruction_{node.uuid.hex}\n")

        # Connection count
        data_.append(f"    dq {len(node.connections)}\n")

        # Store
        data_.append(f"    times 2 dq 0\n")

        # Connections
        for node_, distance in node.connections:
            data_.append(f"    dq node_{node_.uuid.hex}\n")
            data_.append(f"    dq {distance}\n")

        data.append("".join(data_))

    random.shuffle(data)

    data.insert(0, "nodes:\n")
    data.insert(0, "     align 16\n")
    data.insert(0, f"node_count equ {len(nodes)}\n")

    (DIRECTORY / "data.asm").write_text("\n".join(data))

    rodata = []

    rodata.append("    align 16\n\ncheck:\n")
    for i in forward:
        rodata.append(f"    db {i}\n")

    rodata.append("\nig_memory:\n")
    for i in ig.memory:
        for j in i:
            rodata.append(f"    db {j}\n")

    (DIRECTORY / "rodata.asm").write_text("".join(rodata))


if __name__ == "__main__":
    main()
