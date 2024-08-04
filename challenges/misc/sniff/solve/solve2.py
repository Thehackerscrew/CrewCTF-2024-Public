import numpy as np
from PIL import Image

START = b"\x4e\x00\x4f\x00\x00"  # https://github.com/pimoroni/inky/blob/776addf15d60ac720ac29893eeb902f0feea9108/library/inky/inky_ssd1608.py#L208
WIDTH = 250
HEIGHT = 136
BYTES = (WIDTH * HEIGHT) // 8

sequences = []
for sequence in open("solve2.txt").read().split("\n"):
    sequences.append(bytes(int(byte[2:4], 16) for byte in sequence.split()))  # MOSI/MISO

for sequence in sequences:
    if START not in sequence:
        continue
    
    sequence = sequence.split(START)[1]

    black = sequence[1:BYTES+1]
    yellow = sequence[BYTES+2:BYTES*2+2]

    result = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    for image, colour, condition in ((black, (0, 0, 0), 0), (yellow, (255, 255, 0), 1)):
        image = np.unpackbits(np.array(list(image), dtype=np.uint8)).reshape((WIDTH, HEIGHT))
        image = np.rot90(image, 1)

        for y, row in enumerate(image):
            for x, pixel in enumerate(row):
                if pixel == condition:
                    result.putpixel((x, y), colour)

    result.show()
