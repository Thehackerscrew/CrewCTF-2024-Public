# Author Writeup for crymem

## Background

Most crypto challenges are categorized as the following classes:
- theoretical cryptanalysis
- side channel attack
- software vulnerability (weird software specification/implementation bug)

Although I saw some challenges about timing attacks (including the side channel attack class), I have never seen about software-type side channel attack challenges on 1/2 days offline CTF contests.
Then, I tried to create a such type challenge.

An ultimate concept for resisting side channel attacks might be whitebox cryptography.
But designing whitebox-ed cryptosystems are still very hard. I guess "real" whitebox cryptosystems would be emerging further future...

(NOTE: I used to create foolish proprietary whitebox crypto challenge on IJCTF2021. I remember no one did solve it. I will not create such challenges...)

Instead, I considered a weaker (but more realistic) situation:

> "If an attacker obtains a memory dump related to some execution of a cryptographic function, he/she decrypts the ciphertext related to the execution ?"

Thus, I created a forensic-ish challenge (a memory dump with some crypto).

## A Challenge Idea

The most famous crypto library might be OpenSSL.
The OpenSSL library deals with minimizing sensitive information leak carefully.
When [OPENSSL_free](https://www.openssl.org/docs/manmaster/man3/OPENSSL_cleanse.html) is called, OPENSSL contexts are destroyed, not just freed.
So cryptographic keys are vanished on the RAM after cryptographic procedures are ended if those functions properly used.

Conversely, if we forget calling those functions, we can find cryptographic key information on the memory dump!

So I created "vulnerable" encryption function as the following:

```C
int encrypt(uint8_t* out, const uint8_t* in, const uint8_t* key, const uint8_t* iv, int* out_len, in
t in_len) {
    EVP_CIPHER_CTX *ctx;

    if (!(ctx = EVP_CIPHER_CTX_new())) {
        perror("Error creating EVP_CIPHER_CTX\n");
        return -1;
    }

    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, key, iv)) {
        perror("Error initializing encryption\n");
        return -1;
    }

    if (1 != EVP_EncryptUpdate(ctx, out, out_len, in, in_len)) {
        perror("Error during encryption\n");
        return -1;
    }

    //EVP_CIPHER_CTX_free(ctx);

    return 0;
}
```
Clearly, the function has a weird code: commented out `EVP_CIPHER_CTX_free(ctx);`.
We might expect some cryptographic key information is in a memory dump.

## Key Idea to Solve the Challenge

How to extract the AES key from memory dump?
We do not know where the key information exists on the memory dump...

Fortunately, we have the nice tool [AESkeyfind](https://github.com/makomk/aeskeyfind) for searching AES key from a memory dump.

(NOTE: Some tools also implement the similar feature. A famous one is bulk-extractor([specific source code](https://github.com/simsong/bulk_extractor/blob/main/src/scan_aes.cpp#L406)).)

The tool finds candidates of AES keys from raw binary data by using keyexpansion structure.
Many AES libraries (including OpenSSL) uses consecutive memory blocks for keyexpansion.
So we can find AES key effectively by using the tool.

## Brief Writeup

First, applying aeskeyfind.exe to the memory dump:
```bash
$ aeskeyfind/aeskeyfind.exe -t 128 memdump.raw
...
11f9f5aafad8e57c0d14b2e1b52d83d6
...
```

Then, deriving IV and encflag by grep (based on C source code):
```bash
$ strings memdump.raw | grep "IVVALUE"
...
IVVALUE:0ac516e1bc21a36e68932e05ff8aa480
...
$ strings memdump.raw | grep "ENCFLAG"
...
ENCFLAG:caed872aab2b3427778413df7ffa0cb769db2ef567ddc815a3e43a2a0b69b0899a504b198720197c93b897f45313d469
...
```

Finally, decrypt flag! (you can achieve it with various way, but I show simple way with python package)
```python
hexkey = "11f9f5aafad8e57c0d14b2e1b52d83d6"
hexiv = "0ac516e1bc21a36e68932e05ff8aa480"
hexencflag = "caed872aab2b3427778413df7ffa0cb769db2ef567ddc815a3e43a2a0b69b0899a504b198720197c93b897f45313d469"

encflag = bytes.fromhex(hexencflag)
ivvalue = bytes.fromhex(hexiv)
key = bytes.fromhex(hexkey)

from Crypto.Cipher import AES
cipher = AES.new(key, AES.MODE_CBC, iv=ivvalue)
print(cipher.decrypt(encflag))
# b'crew{M3m0ry_f0r3N_is_mysterious_@_crypt0_Challs}'
```

## (Optional Read) How to Have Hardened the Challenge?

I have to avoid unintended solution as much as possible.
More concretelly, I consider the following attack surface:

1. prevent to leak information about key or plaintext with investigating the compiled binary (ELF executable) for encrypting flag
2. prevent to extract `key.txt` or `plaintext.txt` directly
3. prevent to leak information about key or plaintext by using memory blocks which are not related to keyexpansion

For achieving 1st one, I crafted source code not including any hardcoded key or plaintext. And I stripped debug symbols for the binary.

```bash
$ mkdir tmp
$ cp /mnt/hgfs/shared_debian12_ctf_test_1/aes_sample.c tmp # shared folder from host os (using vmware guest os)
$ gcc -o aes_sample.out tmp/aes_sample.c -lssl -lcrypto
$ strip aes_sample.out
$ rm tmp/aes_sample.c

$ cp /mnt/hgfs/shared_debian12_ctf_test_1/plaintext.txt tmp
$ cp /mnt/hgfs/shared_debian12_ctf_test_1/key.txt tmp
```

For achieving 1st and 2nd ones, I removes some history files and then run stress command for scattering RAM:

```bash
$ rm result.txt
$ rm .lesshst
$ rm .bash_history
$ sudo stress --vm-bytes $(awk '/MemTotal/{print $2}' /proc/meminfo)k --vm-keep -m 1 # about 1min
$ sudo reboot
# after reboot...
$ ./aes_sample.out >> result.txt
# after that, suspend the guest os and then obtain memory dump on host os
```

For achieving 3rd ones, I crafted source code. In fact, I added the following functions:

-  `file_read_with_delete` for memory copying directly
- `dummy_file_clear` for destroying local stack memory areas

I do not know the above measurements would be enough to avoid unintended solution, but I trusts reviewed members (forensic enthusiasts team members).
