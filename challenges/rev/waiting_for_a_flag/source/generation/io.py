import struct
from typing import BinaryIO


def write(buffer: BinaryIO, grid: dict[tuple[int, int, int], int]) -> None:
    for (x, y, z), tile in grid.items():
        buffer.write(struct.pack("<lllB", x, y, z, tile))
