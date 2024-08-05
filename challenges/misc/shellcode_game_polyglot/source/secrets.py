from unicorn import *
from setup import *

FLAG = "crew{I_wrote_11-way_polyglot_shellcode_and_all_I_got_was_this_silly_flag_17ecaab3}"

def polymips(index):
  print(f"Level {index}: Polymips")
  print("Your x86_64 shellcode must also be valid MIPS32 shellcode (little endian, N32 ABI only)")
  code = bytes.fromhex(input("Enter your x86_64 shellcode in hex: "))
  
  try:
    run_x86(code)
  except Win:
    run_mips(code)

def up_in_arms(index):
  print(f"Level {index}: Up in ARMs")
  print("Your shellcode must be valid ARMEL shellcode (EABI only)")
  print("Your shellcode must be valid ARMEB shellcode (EABI only)")
  print("Your shellcode must be valid THUMBEL shellcode (EABI only)")
  print("Your shellcode must be valid THUMBEB shellcode (EABI only)")
  code = bytes.fromhex(input("Enter your ARM shellcode in hex: "))
  
  runners = [
    lambda: run_arm(code, UC_MODE_ARM, UC_MODE_LITTLE_ENDIAN),
    lambda: run_arm(code, UC_MODE_ARM, UC_MODE_BIG_ENDIAN),
    lambda: run_arm(code, UC_MODE_THUMB, UC_MODE_LITTLE_ENDIAN),
    lambda: run_arm(code, UC_MODE_THUMB, UC_MODE_BIG_ENDIAN),
  ]
  
  for r in runners:
    try:
      r()
    except Win:
      continue
    break
  else:
    raise Win

def all_together(index):
  print(f"Level {index}: All together now")
  print("Your shellcode must be valid x86_64 shellcode")
  print("Your shellcode must be valid MIPS32 shellcode (little endian, N32 ABI only)")
  print("Your shellcode must be valid MIPS32 shellcode (big endian, N32 ABI only)")
  print("Your shellcode must be valid ARMEL shellcode (EABI only)")
  print("Your shellcode must be valid ARMEB shellcode (EABI only)")
  print("Your shellcode must be valid THUMBEL shellcode (EABI only)")
  print("Your shellcode must be valid THUMBEB shellcode (EABI only)")
  print("Your shellcode must be valid PPC32 shellcode (big endian)")
  print("Your shellcode must be valid RISCV shellcode")
  print("Your shellcode must be valid SPARC32 shellcode (big endian)")
  print("Your shellcode must be valid TriCore shellcode (use syscall 0x45, path in a4)")
  print("Your shellcode will be validated in Unicorn v2.0.1")
  print("Maximum code size is 64k")
  code = bytes.fromhex(input("Enter your x86_64 shellcode in hex: "))
  
  runners = [
    lambda: run_x86(code, PAGE * 16),
    lambda: run_mips(code, UC_MODE_LITTLE_ENDIAN, PAGE * 16),
    lambda: run_mips(code, UC_MODE_BIG_ENDIAN, PAGE * 16),
    lambda: run_arm(code, UC_MODE_ARM, UC_MODE_LITTLE_ENDIAN, PAGE * 16),
    lambda: run_arm(code, UC_MODE_ARM, UC_MODE_BIG_ENDIAN, PAGE * 16),
    lambda: run_arm(code, UC_MODE_THUMB, UC_MODE_LITTLE_ENDIAN, PAGE * 16),
    lambda: run_arm(code, UC_MODE_THUMB, UC_MODE_BIG_ENDIAN, PAGE * 16),
    lambda: run_ppc(code, PAGE * 16),
    lambda: run_riscv(code, PAGE * 16),
    lambda: run_sparc(code, PAGE * 16),
    lambda: run_tricore(code, PAGE * 16),
  ]
  
  for r in runners:
    try:
      r()
    except Win:
      continue
    break
  else:
    raise Win

levels = [polymips, up_in_arms, all_together]
