#from sage.all import *

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

blksize = AES.block_size

from pwn import *
from Crypto.Util.number import *


#proc = process(['sage', '--python', '../server/prob.py'])
proc = remote('localhost', '30001')


F = PolynomialRing(GF(2), 'x')
x = F.gens()[0]
K = GF(2**128, name='a', modulus=x**128+x**7+x**2+x+1)
a = K.gens()[0]
apol = [a**i for i in range(128)]


def bytes_to_apoly(bytestr):
    binlst = list(map(int, bin(bytes_to_long(bytestr))[2:].zfill(128)))
    return sum([bit * apow for bit, apow in zip(binlst, apol)])


def apoly_to_bytes(apoly):
    binstr = ''.join(list(map(str, list(apoly.polynomial()))))
    binstr += '0' * (128-len(binstr))
    bytestr = long_to_bytes(int(binstr, 2))
    if len(bytestr) < blksize:
        bytestr = b'\x00' * (blksize-len(bytestr)) + bytestr
    return bytestr


def comp_H(iv1, enc1, tag1, iv2, enc2, tag2):
    if iv1 != iv2:
        return None
    if len(enc1) != len(enc2) or len(enc1) != 2*blksize:
        return None
    C11, C12 = bytes_to_apoly(enc1[:blksize]), bytes_to_apoly(enc1[blksize:])
    C21, C22 = bytes_to_apoly(enc2[:blksize]), bytes_to_apoly(enc2[blksize:])
    T1 = bytes_to_apoly(tag1)
    T2 = bytes_to_apoly(tag2)
    if C11 != C21:
        return None
    return sqrt((T1-T2)/(C12-C22))


def forge_admindata(curusername, iv, enc, tag, H):
    target = pad(b'admin', blksize)
    xorbyte = lambda x, y: bytes([xele^^yele for xele,yele in zip(x, y)])
    forgeenc = xorbyte(enc[:blksize], xorbyte(curusername[:blksize], target))
    len_A_C = bytes_to_apoly(long_to_bytes(int(bin(0)[2:].zfill(64) + bin(8 * blksize * 2)[2:].zfill(64), 2)))
    C1, C2 = bytes_to_apoly(enc[:blksize]), bytes_to_apoly(enc[blksize:])
    T = bytes_to_apoly(tag)
    ECBENCiv = T - ((C1*H + C2) * H + len_A_C) * H
    forgeC = bytes_to_apoly(forgeenc)
    len_A_forgeC = bytes_to_apoly(long_to_bytes(int(bin(0)[2:].zfill(64) + bin(8 * blksize)[2:].zfill(64), 2)))
    forgeT = ECBENCiv + (forgeC * H + len_A_forgeC) * H
    forgetokenbyte = iv + forgeenc + apoly_to_bytes(forgeT)
    return forgetokenbyte.hex()


def gettoken(ivhex):
    proc.recvuntil(b'option(int): ')
    proc.sendline(b'0')
    proc.recvuntil(b'iv(hex): ')
    proc.sendline(ivhex.encode())
    result = proc.recvline()
    if not (b'token' in result):
        return None
    curusername = result.strip().split(b'token for ')[1].split(b' is:')[0]
    tokenbyte = bytes.fromhex(proc.recvline().strip().decode())
    iv = tokenbyte[:blksize]
    tag = tokenbyte[-blksize:]
    enc = tokenbyte[blksize:-blksize]
    return curusername, iv, enc, tag


_, iv1, enc1, tag1 = gettoken('00'*16)
_, iv2, enc2, tag2 = gettoken('00'*16)
H = comp_H(iv1, enc1, tag1, iv2, enc2, tag2)

curusername, iv, enc, tag = gettoken('11'*16)
forgetokenhex = forge_admindata(curusername, iv, enc, tag, H)

proc.recvuntil(b'option(int): ')
proc.sendline(b'1')
proc.recvuntil(b'token(hex): ')
proc.sendline(forgetokenhex.encode())
print(proc.recvline())
print(proc.recvline())
