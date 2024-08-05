from pwn import *
from time import sleep

KEY_LENGTH = 16

p = remote("atmegapwn.chal.crewc.tf", 1337)

p.sendline(b"encrypt_flag") # retrieve encrypted flag

p.readuntil(b"v2.3\n")

enc_flag = p.readline()[:-1]

p.close()

from Crypto.Cipher import AES

known = list(b"crew{")

flag = [0]*KEY_LENGTH
key = [0]*KEY_LENGTH

for i in range(KEY_LENGTH):
  p = remote("atmegapwn.chal.crewc.tf", 1337)

  for s in range(7):
    # make sure to send the same number of characters every time
    p.sendline((f"secure_erase {i+1}".ljust(15, ' ')).encode())

  sleep(7)

  p.sendline(b"encrypt_flag") # zero out garbage data
  p.sendline(b"encrypt_flag") # actual truncated key

  result = p.readall(timeout=1).split(b"\n")
  
  p.close()
  
  print(result)
  
  partial = result[-2]

  # recover flag byte unless already known
  for c1 in range(256):
    if i < len(known):
      flag[i] = known[i]
    else:
      flag[i] = c1
    
    # recover key byte
    for c2 in range(256):
      key[i] = c2
      cipher = AES.new(bytes(key), AES.MODE_ECB)
      
      ct = cipher.encrypt(bytes(flag))
      
      if ct.hex().encode()[:(i+1)*2] == partial:
        print(bytes(flag))
        print(bytes(key))
        print(ct.hex())
        break
    else:
      if i >= len(known):
        continue
    
    break
  else:
    print("failed to find key :(")
    exit()

cipher = AES.new(bytes(key), AES.MODE_ECB)

print(cipher.decrypt(bytes.fromhex(enc_flag.decode())))
