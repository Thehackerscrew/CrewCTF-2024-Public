your_code = r'''

'''
from pwn import *
import base64
bdata = base64.b64encode(your_code.encode('ascii', 'strict')).decode()


r = remote("127.0.0.1", 1337)

r.sendlineafter('your solve script using base64 encode:', bdata)

r.interactive()