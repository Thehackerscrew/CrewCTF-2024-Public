import math

xor_sequence = [ 204, 82, 149, 44, 105, 166, 154, 5, 56, 192, 22, 13, 80, 138, 151, 184, 31, 187, 74, 221, 110, 138, 66, 229, 155, 37, 147, 238, 210, 159, 202, 121, 30, 124 ]

def divider(r1, r2):
  return r2 / (r1 + r2)

def parallel(rs):
  return 1 / sum([1 / r for r in rs])

def transfer(rs1, rs2):
  return math.floor(divider(parallel(rs1), parallel(rs2)) * 128)

E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

# two decades is enough for intended solution
values = [x * 1 for x in E12] + [x * 10 for x in E12]

def print_flag(top, bottom):
  last_char = 0
  result = ""
  
  for x in xor_sequence:
    v = x ^ last_char
    topv = [t for (i,t) in enumerate(top) if (v & (1 << (i * 2))) != 0]
    botv = [t for (i,t) in enumerate(bottom) if (v & (1 << (i * 2 + 1))) != 0]
    
    if topv == [] or botv == []:
      return
    
    last_char = transfer(topv, botv)
    
    if last_char < 32 or last_char >= 128:
      return
    
    result += chr(last_char)
  
  if result[-1] == '}':
    print(result)

from itertools import product

for (x0,x3,y1) in product(values, repeat=3):
  if transfer([x0, x3], [y1]) == ord('w'):
    for (x1,y3) in product(values, repeat=2):
      if transfer([x1, x3], [y1, y3]) == ord('c'):
        for (y0,y2) in product(values, repeat=2):
          if transfer([x0, x1, x3], [y0, y2, y3]) == ord('e'):
            for x2 in values:
              if transfer([x0, x2], [y2]) == ord('r') and transfer([x1, x2], [y0, y1]) == ord('{'):
                print_flag([x0, x1, x2, x3], [y0, y1, y2, y3])
