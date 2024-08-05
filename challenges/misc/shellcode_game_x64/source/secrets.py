from unicorn import *
from setup import *

FLAG = "crew{got_my_shellcode_and_Im_ready_to_pwn_d3c5891b}"

def anything_goes(index):
  print(f"Level {index}: Anything goes")
  code = bytes.fromhex(input("Enter your x86_64 shellcode in hex: "))
  
  run_x86(code)

def unprintable(index):
  print(f"Level {index}: Unprintable only")
  print("Only unprintable characters allowed! (no ASCII codes 32-126)")
  code = bytes.fromhex(input("Enter your x86_64 shellcode in hex: "))
  
  if not all([c < 32 or c > 126 for c in code]):
    print("Printable characters found")
    raise Exception()
  
  run_x86(code)

def palindrome(index):
  print(f"Level {index}: Palindrome")
  print("Your shellcode must be a palindrome")
  code = bytes.fromhex(input("Enter your x86_64 shellcode in hex: "))
  
  if not all([code[i] == code[len(code)-i-1] for i,_ in enumerate(code)]):
    print("Not a palindrome")
    raise Exception()
  
  run_x86(code)

def real_palindrome(index):
  print(f"Level {index}: Real Palindrome")
  print("Your shellcode must be a palindrome (no dead code!)")
  code = bytes.fromhex(input("Enter your x86_64 shellcode in hex: "))
  
  if not all([code[i] == code[len(code)-i-1] for i,_ in enumerate(code)]):
    print("Not a palindrome")
    raise Exception()
  
  visited = [False]*PAGE
  
  def setup(uni,code_addr):
    def hook(uni,addr,size,_):
      for i in range(size):
        visited[addr - code_addr + i] = True
    
    uni.hook_add(UC_HOOK_CODE, hook)
    
    return code_addr
  
  try:
    run_x86(code, setup = setup)
  except Win:
    if all(visited[:len(code)]):
      raise Win
    else:
      print("Dead code detected")

def sixteen_bit(index):
  print(f"Level {index}: 16-bit era")
  print("Your shellcode cannot execute instructions longer than 16 bits")
  code = bytes.fromhex(input("Enter your x86_64 shellcode in hex: "))
  
  visited = [False]*PAGE
  
  def setup(uni,code_addr):
    def hook(uni,addr,size,_):
      if size > 2:
        raise Exception()
    
    uni.hook_add(UC_HOOK_CODE, hook)
    
    return code_addr
  
  run_x86(code, setup = setup)

def prime_time(index):
  print(f"Level {index}: Prime Time")
  print("Non-zero bytes in your shellcode must be one of the prime numbers < 256")
  code = bytes.fromhex(input("Enter your x86_64 shellcode in hex: "))
  
  primes = [0, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251]
  
  if not all([(c in primes) for c in code]):
    print("Non-prime found")
    raise Exception()
  
  run_x86(code)

def whatslide(index):
  print(f"Level {index}: A Whatslide?")
  print("Your shellcode must be valid no matter where execution starts")
  print("You get 3 free bytes at the end, all other bytes must be valid entry points")
  code = bytes.fromhex(input("Enter your x86_64 shellcode in hex: "))
  
  wins = [False]*(len(code)-3)
  
  for i in range(len(code)-3):
    try:
      run_x86(code, setup = lambda u,p: p+i)
    except Win:
      wins[i] = True
      continue
    break
  
  if len(wins) > 0 and all(wins):
    raise Win

levels = [anything_goes, unprintable, palindrome, real_palindrome, sixteen_bit, prime_time, whatslide]
