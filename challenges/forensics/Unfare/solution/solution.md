# Unfare
Someone was reading cards on my computer! Lucky I was listening... 

The flag is in this format: `crew{[a-z0-9!_]+}`.

## Answer

Identify the software by packet 51 by looking up the verison.

You can find the block by tracking byte 35 on packets like 161 to see what block is being read in read requests from the Proxmark3. 

The `20 06` are the bytes which start the communication in both requests and responses, proceeded afterwards by the block number (in requests).

If you read the first data bytes in order of what blocks need to be read, you will get the flag.

The blocks are read in a random order so you can't follow it sequentially, you have to find the changing byte and work with it.

### Solve Script
```python
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
```

The code isn't too clean, the best solution was provided by a participant (imo) (thank you warlocksmurf).

Flag: `crew{s3al_mak3_flag_l0ng_t0_c0v3r_th3s3_bl0cks!}`

Reading Material: https://github.com/RfidResearchGroup/proxmark3/blob/master/doc/new_frame_format.md
