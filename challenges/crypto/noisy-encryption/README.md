# Noisy Encryption (3 solves)

I can encrypt your messages, however, I will reveal just a little bit of information ...

# Writeup

Suppose that we have a number X such that $X>=2^{3b}$ and $X<2^{3b-1}$, and with query $i$, where $0\leq i$ and $i<2^b$, we know the parity of the hamming weight of $X-i^3$.
If we query for all $i$, with $b=5$, we can determine the number uniquely with 75% probability, and in the other cases there are only two possibilities, so we might recover some bits of $X$. To avoid recomputation, we store the answers in a dictionary.

Since we know that $N$ has a set bit in position 1023, we can thus use this strategy by asking numbers on the form $n-a2^b$, which returns the parity of the hamming weight of $n-a^3 2^{3b}$. Unfortunately this strategy is not enough, so we can generalize it with strategies where we assume $2^{3b} U \leq X < 2^{3b}(U+1)$ for $U=1,2,4$ to almost always recover the number n.

For more accuracy, we could bruteforce over the remaining possibilities for $n$, however this was not necessary.
