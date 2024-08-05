import math
from queue import PriorityQueue
import string

charset = string.printable.encode()

digits = "123A456B789C*0#D"

dim = math.isqrt(len(digits))

def angle(a,b):
  x0 = a % dim
  y0 = a // dim
  
  x1 = b % dim
  y1 = b // dim
  
  deg = math.degrees(math.atan2(y1 - y0, x1 - x0))
  
  if deg < 0:
    deg = deg + 360
  
  return deg

angles = [[angle(a,b) for b in range(len(digits))] for a in range(len(digits))]

from wand.image import Image
from wand.color import Color

seq = []

def colordiff(a,b):
  return abs(a.red - b.red) + abs(a.green - b.green) + abs(a.blue - b.blue)

with Image(filename='pin.gif') as image:
  for i in image.sequence[:-1]: # last frame contains no new information
    for a in set(sum(angles, [])):
      samples = [(a,9),(a+18,7),(a-18,7)] # look for the edges of the triangle indicator
      
      if all([colordiff(Image(i)[round(23 + math.cos(math.radians(s[0])) * s[1]),round(23 + math.sin(math.radians(s[0])) * s[1])], Color("black")) > 0.1 for s in samples]):
        seq.append(a)
        break
    else:
      assert(False)

def frompin(p,b,n):
  print(p)

  if len(p) == 0:
    return 0

  return b.find(p[0]) * n + frompin(p[1:], "".join([c for c in digits if c != p[0]]), n * len(b))

def decode(r):
  result = frompin("".join([digits[d] for d in r]), digits, 1)
  return result.to_bytes((result.bit_length() + 7) // 8, 'big')

q = PriorityQueue()

for dig in range(len(digits)):
  q.put((-1, [dig]))

def prune(r):
  p = r

  while len(p) < len(seq)+1:
    p = [(p[0] + 1) % 16] + p

  return not all([c in charset for c in decode(p)[:int(len(r)/2.05)]])

# DFS
while not q.empty():
  (_,r) = q.get()
  
  if prune(r): # remove solutions which would contain unprintable characters
    continue
  
  if len(r) == len(seq) + 1:
    d = decode(r)
    
    if all([c in charset for c in d]) and d[:5] == b"crew{" and d[-1:] == b"}":
      print(d)
    
    continue
  
  for dig in range(len(digits)):
    if dig != r[0]:
      deg = angle(dig, r[0])
      
      if abs(deg - seq[-len(r)]) < 0.1:
        q.put((-(len(r)+1), [dig] + r))
