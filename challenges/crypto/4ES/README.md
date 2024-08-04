# 4ES (90 solves)

- **Author: 7Rocky**
- **Difficulty: easy**
- **Theme: AES, MITM**

### Description

AES is very robust, but let's quadruple its power!

## Writeup

We are given a Python script that encrypts the flag 4 times with AES. The 4 AES keys are SHA256 hashes of three-word choices from a given alphabet: `crew_AES*4=$!?`. We are also given a plaintext `AES_AES_AES_AES!` and its ciphertext.

In brief, we have 3-word keys from a 14-word alphabet that are hashed and 4 encryptions. A naïve brute force attack would take up to $(14^3)^4 = 14^{12}$ possibilities, that is $2^{45} \lt 14^{12} \lt 2^{46}$, which is not affordable.

Instead, we can use a meet-in-the-middle (MITM) attack. That is, instead of computing 4 forward encryptions, we can compute 2 forward encryptions, save them in a look-up table and then perform 2 backward decryptions until we find a match. The complexity of this approach will be $2 \cdot (14^3)^2 = 2 \cdot 14^6$ possibilities, which is affordable because $2^{23} \lt 2 \cdot 14^6 \lt 2^{24}$.

So, we will have a map:

$$
\mathrm{ENC}\_{k_1}(\mathrm{ENC}\_{k_2}(\mathrm{pt})) \to (k_1, k_2)
$$

And we test $\mathrm{DEC}\_{k_4}(\mathrm{DEC}\_{k_3}(\mathrm{ct}))$ until we find a match. At that point, we will have $(k_1, k_2, k_3, k_4)$ so that 

$$
\mathrm{ct} = \mathrm{ENC}\_{k_1}(\mathrm{ENC}\_{k_2}(\mathrm{ENC}\_{k_3}(\mathrm{ENC}\_{k_4}(\mathrm{pt}))))
$$

and

$$
\mathrm{pt} = \mathrm{DEC}\_{k_4}(\mathrm{DEC}\_{k_3}(\mathrm{DEC}\_{k_2}(\mathrm{DEC}\_{k_1}(\mathrm{ct}))))
$$

The solvers are single-threaded and not optimized. One of them is programmed in Go, which takes around 10 seconds to run; whereas the Python solver takes around 2 minutes:

```console
$ time go run solve.go
crew{m1tm_at74cK_1s_g0lD_4nd_py7h0n_i5_sl0w!!}
go run solve.go  18,50s user 0,63s system 201% cpu 9,475 total

$ time python3 solve.py 
crew{m1tm_at74cK_1s_g0lD_4nd_py7h0n_i5_sl0w!!}
python3 solve.py  94,24s user 0,33s system 99% cpu 1:35,16 total
```
