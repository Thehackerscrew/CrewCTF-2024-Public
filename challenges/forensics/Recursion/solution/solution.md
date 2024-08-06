# Recursion
I caught my co-worker moving some weird files on a USB, can you tell me whats going on?

## Answer
Looking at the PCAP there is the file data in packet 55. Its a .gz file, which has a PCAPNG inside.

Next one has a .7z in Packet 59.

Next one is a .tar in Packet 51.

Next one is a .zip in Packet 67.

Last one is a plain .pcapng in Packet 59.

Flag is in Packet 67.

Flag: `crew{l00ks_l1ke_y0u_mad3_1t!}`

> This process can be way quicker with `binwalk -e`.