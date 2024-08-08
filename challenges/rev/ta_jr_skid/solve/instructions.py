import struct


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
