import subprocess
import base64
import tempfile
import shutil
import os
from secrets import FLAG

forbidden = ['fun', 'use', 'module', '#', 'assert', 'test']

solve_script = input("your solve script using base64 encode: ")
decoded_script = base64.b64decode(solve_script).decode('ascii', 'strict')


if any(keyword in decoded_script for keyword in forbidden):
    raise ValueError("Script contains forbidden keywords!")

chall_path = "/home/user/chall"

with tempfile.TemporaryDirectory() as temp_dir:
    dest_folder = os.path.join(temp_dir, os.path.basename(chall_path))
    shutil.copytree(chall_path, dest_folder)
    
    file_path = os.path.join(dest_folder, "sources/solve.move")

    start_line = 18

    with open(file_path, 'r', encoding='ascii') as file:
         lines = file.readlines()
    
    lines.insert(start_line - 1, decoded_script + '\n')
    
    with open(file_path, 'w', encoding='ascii') as file:
        file.writelines(lines)


    result = subprocess.run(f"cd {dest_folder};sui move test --gas-limit 10000000000 --silence-warnings --no-lint", shell=True, capture_output=True, timeout=15).stdout.decode()
    print(result)
    result = result.split('\n')
    if result[-3] == "[ PASS    ] 0x0::poc::poc" and result[-2] == "Test result: OK. Total tests: 1; passed: 1; failed: 0":
        print("congrats!")
        print(FLAG)
    else:
        print("wrong!")