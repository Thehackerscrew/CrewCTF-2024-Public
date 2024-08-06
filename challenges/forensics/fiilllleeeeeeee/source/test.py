from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from hashlib import sha256
from pathlib import Path

public_key = X25519PublicKey.from_public_bytes(bytes.fromhex("6dddeb063f0d61967801f1f17520884130808408dd234886aa6322d52f4e8a5c"))
private_key = X25519PrivateKey.from_private_bytes(bytes.fromhex("98517416b163f37fc152d765fbd4898acf8a07a554f25fe3814374533b9d916c"))

shared_key = sha256(private_key.exchange(public_key)).digest()

print(shared_key.hex())

flag_enc = (Path(__file__).parent.parent / "dist" / "flag.txt").read_bytes()

nonce = flag_enc[16:16 + algorithms.AES256.block_size // 8]

cipher = Cipher(algorithms.AES256(shared_key), modes.CTR(nonce))
decyptor = cipher.decryptor()

print(decyptor.update(flag_enc[16 + algorithms.AES256.block_size // 8:]) + decyptor.finalize())
