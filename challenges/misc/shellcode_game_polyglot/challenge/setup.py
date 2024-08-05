from unicorn import *
from unicorn.x86_const import *
from unicorn.mips_const import *
from unicorn.arm_const import *
from unicorn.ppc_const import *
from unicorn.riscv_const import *
from unicorn.sparc_const import *
from unicorn.tricore_const import *
from random import getrandbits
import gc

PAGE = 0x1000
RX = UC_PROT_READ | UC_PROT_EXEC
RW = UC_PROT_READ | UC_PROT_WRITE
RWX = UC_PROT_READ | UC_PROT_WRITE | UC_PROT_EXEC

def strcmp(uni, address, string):
  return all([c == chr(uni.mem_read(address+i, 1)[0]) for (i,c) in enumerate(string+"\x00")])

class Win(Exception):
  pass

def init_uni(arch, mode, code, code_size, aslr_bits, page_size = PAGE, code_prot = RWX, stack_prot = RWX):
  gc.collect()
  
  code_addr = (1 + getrandbits(aslr_bits)) * page_size
  stack_addr = (getrandbits(aslr_bits) + 2**(aslr_bits+2)) * page_size
  
  uni = Uc(arch, mode)
  uni.mem_map(code_addr, code_size, code_prot)
  uni.mem_map(stack_addr, page_size * 2, stack_prot)
  
  uni.mem_write(code_addr, code)
  
  return (uni, code_addr, stack_addr)

def run_x86(code, code_size = PAGE, code_prot = RWX, stack_prot = RWX, setup = lambda u,p: p):
  (uni, code_addr, stack_addr) = init_uni(UC_ARCH_X86, UC_MODE_64, code, code_size, 30)
  
  uni.reg_write(UC_X86_REG_RSP, stack_addr + PAGE)
  
  def hook_syscall(uni, user_data):
    if uni.reg_read(UC_X86_REG_RAX) == 59:
      if strcmp(uni, uni.reg_read(UC_X86_REG_RDI), "/win"):
        raise Win
    
    raise Exception
  
  uni.hook_add(UC_HOOK_INSN, hook_syscall, None, 1, 0, UC_X86_INS_SYSCALL)
  
  code_addr = setup(uni, code_addr)
  
  uni.emu_start(code_addr, code_addr + code_size)

def run_mips(code, endianness = UC_MODE_LITTLE_ENDIAN, code_size = PAGE, code_prot = RWX, stack_prot = RWX, setup = lambda u,p: p):
  (uni, code_addr, stack_addr) = init_uni(UC_ARCH_MIPS, UC_MODE_MIPS32 + endianness, code, code_size, 16)
  
  uni.reg_write(UC_MIPS_REG_SP, stack_addr + PAGE)
  
  def hook_syscall(uni, intr, user_data):
    if intr == 17: # syscall
      if uni.reg_read(UC_MIPS_REG_V0) == 5057:
        if strcmp(uni, uni.reg_read(UC_MIPS_REG_A0), "/win"):
          raise Win
    
    raise Exception
  
  uni.hook_add(UC_HOOK_INTR, hook_syscall)
  
  code_addr = setup(uni, code_addr)
  
  uni.emu_start(code_addr, code_addr + code_size)

def run_arm(code, mode = UC_MODE_ARM, endianness = UC_MODE_LITTLE_ENDIAN, code_size = PAGE, code_prot = RWX, stack_prot = RWX, setup = lambda u,p: p):
  (uni, code_addr, stack_addr) = init_uni(UC_ARCH_ARM, mode + endianness, code, code_size, 16)
  
  uni.reg_write(UC_ARM_REG_SP, stack_addr + PAGE)
  
  def hook_syscall(uni, intr, user_data):
    if intr == 2: # svc 0
      if uni.reg_read(UC_ARM_REG_R7) == 11:
        if strcmp(uni, uni.reg_read(UC_ARM_REG_R0), "/win"):
          raise Win
    
    raise Exception
  
  uni.hook_add(UC_HOOK_INTR, hook_syscall)
  
  code_addr = setup(uni, code_addr)
  
  uni.emu_start(code_addr + (1 if mode == UC_MODE_THUMB else 0), code_addr + code_size)

TC_PAGE = 0x10000

def run_tricore(code, code_size = TC_PAGE, code_prot = RWX, stack_prot = RWX, setup = lambda u,p: p):
  (uni, code_addr, stack_addr) = init_uni(UC_ARCH_TRICORE, UC_MODE_LITTLE_ENDIAN, code, code_size, 16, TC_PAGE)
  
  uni.reg_write(UC_TRICORE_REG_SP, stack_addr + TC_PAGE)
  
  def hook_syscall(uni,addr,size,_):
    if int.from_bytes(uni.mem_read(addr, size), 'little') & 0x0FFFF0FF == 0x008450ad:
      if strcmp(uni, uni.reg_read(UC_TRICORE_REG_A4), "/win"):
        raise Win
  
  uni.hook_add(UC_HOOK_CODE, hook_syscall)
  
  code_addr = setup(uni, code_addr)
  
  uni.emu_start(code_addr, code_addr + code_size)

def run_ppc(code, code_size = PAGE, code_prot = RWX, stack_prot = RWX, setup = lambda u,p: p):
  (uni, code_addr, stack_addr) = init_uni(UC_ARCH_PPC, UC_MODE_PPC32 + UC_MODE_BIG_ENDIAN, code, code_size, 16)
  
  uni.reg_write(UC_PPC_REG_1, stack_addr + PAGE)
  
  def hook_syscall(uni, intr, user_data):
    if intr == 8: # syscall
      if uni.reg_read(UC_PPC_REG_0) == 11:
        if strcmp(uni, uni.reg_read(UC_PPC_REG_3), "/win"):
          raise Win
    
    raise Exception
  
  uni.hook_add(UC_HOOK_INTR, hook_syscall)
  
  code_addr = setup(uni, code_addr)
  
  uni.emu_start(code_addr, code_addr + code_size)

def run_riscv(code, code_size = PAGE, code_prot = RWX, stack_prot = RWX, setup = lambda u,p: p):
  (uni, code_addr, stack_addr) = init_uni(UC_ARCH_RISCV, UC_MODE_RISCV32, code, code_size, 16)
  
  uni.reg_write(UC_RISCV_REG_SP, stack_addr + PAGE)
  
  def hook_syscall(uni, intr, user_data):
    if intr == 8: # syscall
      if uni.reg_read(UC_RISCV_REG_A7) == 221:
        if strcmp(uni, uni.reg_read(UC_RISCV_REG_A0), "/win"):
          raise Win
    
    raise Exception
  
  uni.hook_add(UC_HOOK_INTR, hook_syscall)
  
  code_addr = setup(uni, code_addr)
  
  uni.emu_start(code_addr, code_addr + code_size)

def run_sparc(code, code_size = PAGE, code_prot = RWX, stack_prot = RWX, setup = lambda u,p: p):
  (uni, code_addr, stack_addr) = init_uni(UC_ARCH_SPARC, UC_MODE_SPARC32 + UC_MODE_BIG_ENDIAN, code, code_size, 16)
  
  uni.reg_write(UC_SPARC_REG_SP, stack_addr + PAGE)
  
  def hook_syscall(uni, intr, user_data):
    if intr == 144: # syscall
      if uni.reg_read(UC_SPARC_REG_G1) == 59:
        if strcmp(uni, uni.reg_read(UC_SPARC_REG_O0), "/win"):
          raise Win
    
    raise Exception
  
  uni.hook_add(UC_HOOK_INTR, hook_syscall)
  
  code_addr = setup(uni, code_addr)
  
  uni.emu_start(code_addr, code_addr + code_size)
