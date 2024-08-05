# Boring LCG (12 solves)

- **Author: Blupper**
- **Difficulty: Medium**
- **Theme: LCG, LLL**

### Description

Just your average LCG challenge

## Writeup

The challenge amounts to recovering the seed for an LCG with known parameters over the field $\mathbb{F}_{p^3}$ where $p$ is a 64-bit prime. Note that this is absolutely not the same as working modulo $p^3$, a finite field of order $p^k$ is instead instead usually constructed as a polynomial ring with coefficients in $\mathbb{F}_p$ modulo an irreducible polynomial of degree $k$, i.e $\mathbb{F}_p [i] / p(x)$

Each element can be represented as $a + bi + ci^2$ where $i$ is the polynomial indeterminate, we are given the highest 7 bits of each of the three coefficients for 12 consecutive outputs of the LCG.

## Simplifying
If this was just an LCG over $\mathbb{F}_p$ with multiplier $a$ and increment $b$ we could use the following approach:

The $i$ th LCG output will be of the form $s_i = a^i s_0 + b \frac{a^i-1}{a-1}$ where $s_0$ is the initial seed. This can be derived by looking at the expansion and using the sum of a geometric series.

Let $B_i = b \frac{a^i-1}{a-1}$ be the constant term of each output, and construct the lattice spanned by the rows of:

$$
\begin{bmatrix}
1 & a^1 & a^2 & \cdots & a^n \\
0 & p & 0 & \cdots & 0 \\
0 & 0 & p & \cdots & 0 \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
0 & 0 & 0 & \cdots & p \\
\end{bmatrix}
$$

If we multiply this matrix on the left by $[s_0, k_1, k_2, ..., k_n]$ with $k_i$ which minimize the result the result will be of the form $[s_0, s_1 - B_1, s_2 - B_2]$. If we let $h_i$ be the midpoint of the largest and smallest possible value of $s_i$ (deduced from our given bits) then we can try to find a close vector in this lattice to $[h_0, h_1 - B_1, ..., h_n - B_n]$ and hope that it finds the previously mentioned vector, in which case the seed will be in the first entry. This can be done using Babai's nearest plane algorithm or LLL embedding.

## The crux

Here we are not working in $\mathbb{F}_p$ but $\mathbb{F}_{p^3}$, we need to extend the above lattice approach to this domain.

If we expand each entry into three different columns, one for each coefficient of the polynomial, then addition of vectors works as expected. We however want to be able to multiply each row by not only an integer (which is what LLL does by default) but by another element of $\mathbb{F}_{p^3}$. On top of the new row $v$ we thus also need to add $vi$ and $vi^2$ to the basis, this will extend our span to be the same. This is all that's needed to solve the chall, see [solve.py](./solve/solve.py) for details.