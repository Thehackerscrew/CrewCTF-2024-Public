# Read between the lines

- **Author: 7Rocky**
- **Difficulty: easy**
- **Theme: RSA, LLL**

### Description

Small numbers and RSA do not get on well, but can I group them together?

## Writeup

We are given a Python script that uses some sort of RSA to encrypt the flag.

First, the flag is encoded as the index of the flag character $i + \mathtt{0x1337}$ repeated $b_i$ times, where $b_i$ is the ASCII value of the $i$-th character:

```python
encoded_flag = []

for i, b in enumerate(FLAG):
    encoded_flag.extend([i + 0x1337] * b)
```

This `encoded_flag` is shuffled, but it is irrelevant as we will see later:

```python
shuffle(encoded_flag)
```

Then this is the ciphertext:

```python
e = 65537
p, q = getPrime(1024), getPrime(1024)
n = p * q
c = sum(pow(m, e, n) for m in encoded_flag) % n
```

So, in math terms we have:

$$
c = \sum_{m \in \mathtt{encoded\_flag}} m^e \mod{n}
$$

Remember that each $m$ in `encoded_flag` is $i + \mathtt{0x1337}$ repeated $b_i$ times, so we have

$$
c = \sum_{i = 0}^{N - 1} b_i \cdot (i + \mathtt{0x1337})^e \mod{n}
$$

Where $N$ is the flag length and $b_i$ is the $i$-th character of the flag. Notice that the shuffling is irrelevant because addition is commutative, so the order does not matter.

We can express $c$ as follows:

$$
c = b_0 (0 + \mathtt{0x1337})^e + b_1 (1 + \mathtt{0x1337})^e + \dots + b_{N - 1} (N - 1 + \mathtt{0x1337})^e \mod{n}
$$

Observe that we can pre-compute $(i + \mathtt{0x1337})^e \mod{n}$, we want to find the coefficients $b_i$. For this, we can use a lattice technique such as LLL.

First of all, we will get rid of $\mod{n}$ to work over the integers, so for some $k \in \mathbb{Z}$ we have:

$$
b_0 (0 + \mathtt{0x1337})^e + b_1 (1 + \mathtt{0x1337})^e + \dots + b_{N - 1} (N - 1 + \mathtt{0x1337})^e + k \cdot n - c = 0
$$

Now, we will use the lattice spanned by the columns of

$$
M = \begin{pmatrix}
  (0 + \mathtt{0x1337})^e & (1 + \mathtt{0x1337})^e & \dots  & (N - 1 + \mathtt{0x1337})^e & n      & -c     \\
  1                       & 0                       & \dots  & 0                           & 0      & 0      \\
  0                       & 1                       & \dots  & 0                           & 0      & 0      \\
  \vdots                  &                         & \ddots & \vdots                      & \vdots & \vdots \\
  0                       & 0                       & \dots  & 1                           & 0      & 0      \\
  0                       & 0                       & \dots  & 0                           & 1      & 0      \\
  0                       & 0                       & \dots  & 0                           & 0      & R      \\
\end{pmatrix}
$$

Where $R$ is an arbitrarily large number such as $R = 2^{1024}$. The target vector is $(0, b_0, b_1, \dots, b_{N - 1}, k, R)$, which belongs to the lattice because:

$$
\begin{pmatrix}
  (0 + \mathtt{0x1337})^e & (1 + \mathtt{0x1337})^e & \dots  & (N - 1 + \mathtt{0x1337})^e & n      & -c     \\
  1                       & 0                       & \dots  & 0                           & 0      & 0      \\
  0                       & 1                       & \dots  & 0                           & 0      & 0      \\
  \vdots                  &                         & \ddots & \vdots                      & \vdots & \vdots \\
  0                       & 0                       & \dots  & 1                           & 0      & 0      \\
  0                       & 0                       & \dots  & 0                           & 1      & 0      \\
  0                       & 0                       & \dots  & 0                           & 0      & R      \\
\end{pmatrix} \cdot \begin{pmatrix}
  b_0       \\
  b_1       \\
  \vdots     \\
  b_{N - 1} \\
  k         \\
  1         \\
\end{pmatrix} = \begin{pmatrix}
  0         \\
  b_0       \\
  b_1       \\
  \vdots     \\
  b_{N - 1} \\
  k         \\
  R         \\
\end{pmatrix}
$$

And since the target vector is short (because all $0 \leqslant b_i \lt 256$), we can find it using LLL on the matrix $M$. We can use the $R$ to find the target vector on the reduced lattice matrix:

```python
N = 100
cts = [pow(m + 0x1337, e, n) for m in range(N)]

R = 2 ** 1024
M = Matrix([
    [*cts, n, -c],
    *[[0] * i + [1] + [0] * (len(cts) - i + 1) for i in range(len(cts))],
    [0] * len(cts) + [0, R]
])

L = M.T.LLL()
assert L[-1][0] == 0 and L[-1][-1] == R
res = L[-1][1:-1]

flag = [v for v in res if v != 0]
print(bytes(flag).decode())
```

With this, we will have the flag:

```console
$ python3 solve.py
crew{D1d_y0u_3xp3cT_LLL_t0_b3_h1Dd3n_b3tw3en_th3_l1n3s???}
```
