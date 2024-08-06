from pcapng import FileScanner
from pcapng.blocks import EnhancedPacket
curBlock=""
card_data = []
for x in range(64):
    card_data.append(b"")
c=0
with open('traffic.pcapng', 'rb') as fp:
    scanner = FileScanner(fp)
    for block in scanner:
        if isinstance(block, EnhancedPacket):
            data = block.packet_data
            if b'\x20\x06' in data:
                if block.packet_len == 45:
                    blkid = data.split(b'\x20\x06')[1][0]
                    curBlock=blkid
                elif block.packet_len == 55:
                    blk = data.split(b'\x20\x06')[1].split(b'\x62\x33')[0]
                    if curBlock != "":
                        c+=1
                        card_data[curBlock] = blk[:1]
print(b''.join(card_data).decode('utf8'))