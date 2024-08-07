# admin (14 solves)

- **Author: kiona**
- **Difficulty: middle**
- **Theme: AES GCM mode**

## description

get admin access.

## Writeup

### Challenge Overview

When we connect the server, we can select two option:
- 0: givetoken
  
  With provided IV, the server creates token (ciphertext and tag for `curusername` with AES-GCM mode), where `urusername = b'not_admin_username_' + str(i).encode()` (`i` is a counter of calling givetoken)
- 1: checktoken

  With provided token, check whether the token is for `b"admin"`. If so, you will obtain the flag.

So the goal is to forge token for "admin" from the information of tokens for "not_admin_username0", "not_admin_username1", etc.

### Main Vulnerability

GCM mode provides both of confidentiality and authenticity. For providing authenticity, it creates a tag with GHASH, which is defined over the finite field or Galois field.

It is well-known that IV reuse would break some cryptosystems. If IV is reused on GCM mode, the authenticity would be broken.

Also, the ciphertext part is an application of CTR mode. CTR mode is weak about XOR operation attack if IV reused.

See the solve script for detail.

