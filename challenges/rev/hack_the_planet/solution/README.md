# Hack the Planet

Javascript is obfuscated with jsfuck, hooking eval will recover the original code.

The goal is to recover the set of 16 transformation matrices which will produce a correct rendering of the earth.

A comment in the deobfuscated JS code points to the source of the original vertex data, UV coordinates are untransformed so a 1:1 mapping can be made.

There are several sets of matrices which would lead to a correct rendering but only one is reachable in practice due to the way the flag is XORed with the data.

Solve script is not super clean, someone with better math skills might be able to devise a better solution :)
