# SPI:
# - MOSI = 6
# - Clock = 7
# - Enable = 8

from time import sleep

from inky.auto import auto
from PIL import Image
from smbus import SMBus

FLAG1 = b"flag{717f7532}"

def convert(image):
    converted = Image.new("L", image.size)

    data = []
    for pixel in image.getdata():
        best = None
        for colour, value in (((255, 255, 255), 0), ((0, 0, 0), 1), ((255, 255, 0), 2)):
            difference = sum(abs(pixel[i] - colour[i]) for i in range(3))
            if best is None or (difference) < best[0]:
                best = difference, value

        data.append(best[1])
    
    converted.putdata(data)
    return converted


def main():
    display = auto()

    display.set_image(convert(Image.open("prompt.png")))
    display.show()

    i2c = SMBus(1)

    password = bytearray()
    while True:
        # Read from the keyboard.
        try:
            byte = i2c.read_byte(0x5f)
        except OSError:
            pass

        if byte not in (0x00, 0x80):
            if byte == 0x08:
                try:
                    del password[-1]
                except IndexError:
                    pass
                print(password)
            elif byte == 0x0d:
                if password == FLAG1:
                    display.set_image(convert(Image.open("flag2.png")))
                    display.show()
                else:
                    password.clear()
            else:
                password.append(byte)
                print(password)
        
        sleep(0.1)

if __name__ == "__main__":
    main()
