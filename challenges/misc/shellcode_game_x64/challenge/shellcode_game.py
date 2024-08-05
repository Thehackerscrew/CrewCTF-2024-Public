from secrets import FLAG, levels
from setup import Win

print("Welcome to The Shellcode Game!")
print("In this game you must submit linux shellcode which runs execve(\"/win\")")
print("Address space randomization is enabled")
print("Privilege levels are not enforced, privileged instructions may be ignored")
print("Maximum code size is 4k")
print("x86 syscalls should be made using the 64-bit ABI")
print("The shellcode you submit must conform to the given specification")
print(f"Each level has different rules, there are {len(levels)} levels in total")

for index,level in enumerate(levels):
  print("")
  
  try:
    level(index+1)
  except Win:
    print("You win!")
    continue
  except:
    pass
  
  print("You lose :(")
  exit()

print("Congratulations, you have beaten all the levels!")
print(f"Here is your reward: {FLAG}")
