import sys
import os
import subprocess
import tempfile
import shutil

from secrets import FLAG

SECRET = os.urandom(16)

secret_script = "\r".join(["f 0000:02%02x 2%02x %02x" % (i,i,b) for (i,b) in enumerate(SECRET)]) + "\rQ\r"

tempdir = tempfile.TemporaryDirectory()

shutil.copy("DEBUG.EXE", tempdir.name) # DEBUG.EXE from MS-DOS 5.0, unmodified

open(tempdir.name + "/secret.dsf", "w").write(secret_script)

print("The secret is at address 0000:0200 in memory.")
print("There is no memory protection so just go ahead and read it ¯\_('_')_/¯")
print("Enter your DEBUG script, end with a line containing only 'Q':")

debug_script = ""

while True:
  line = sys.stdin.readline().strip()
  
  debug_script = debug_script + line + "\r" # DOSBox + DEBUG + linefeed = bad
  
  if line == "Q":
    break

open(tempdir.name + "/input.dsf", "w").write(debug_script)

cmds = [
  "mount c: " + tempdir.name,
  "config -securemode",
  "c:",
  "debug < secret.dsf",
  "del secret.dsf",
  "debug < input.dsf",
  "exit",
]

args = ["dosbox"] + sum([["-c", cmd] for cmd in cmds], [])

subprocess.run(args, timeout = 10)

if input("What was the secret? ") == SECRET.hex():
  print(f"That is correct! Here is your flag: {FLAG}")
else:
  print("Sorry that's not correct, better luck next time!")
