# Bigger and better (7 solves)
Author: Babafaba

### Description

Bigger numbers, more variables, go big or go home.

## Writeup

We are given a `source.sage` file whose functionality can be briefly summarized as:
- A random key made up of 150 random alphanumeric characters is generated
- the key is split into 5 parts `V, W, X, Y, Z` 
- A random 5-variate polynomial over Zmod(n) is generated, where n is a huuuuuge composite number of the form $`n=(p_1*p_2*p_3*p_4)^2`$, where $`p_i`$ are 4096-bit primes
- The polynomial is evaluated at the point defined by the 5 parts of the splitted key and its constant term tweaked so those 5 values are a root.
- the original key is hashed and then used to encrypt the flag

Additionally, an `output.txt` file is provided that contains:
- The size of the 5 parts(30 bytes, since they're ascii the MSB is 0 so roughly $`30*8-1 = 239`$ bits)
- The modulus `n`
- The polynomial
- The encrypted flag

Relavant code from the source file:
```python
polsize = 25
maxexp = 3

V, W, X, Y, Z = [bytes_to_long(b) for b in [key[blocklen*i:blocklen*i+blocklen] for i in range(5)]]

n = getPrime(4096)*getPrime(4096)*getPrime(4096)*getPrime(4096)
n = n^2

K = Zmod(n)
PP.<v, w, x, y, z> = PolynomialRing(K)

coeffs = [K.random_element() for i in range(polsize)]

pol = 0
for l in range(polsize):
    while True:
        i, j, k, s, t = [randbelow(maxexp) for _ in range(5)]
        if i == j == k == s == t == 0: continue
        pol = pol + coeffs[l] * v^i * w^j * x^k * y^s * z^t
        if len(pol.coefficients()) == l + 1:
            break

c = pol(V, W, X, Y, Z)
pol = pol - c
```
It is clear the goal is to find that root of the polynomial to reconstrunct the original key and decrypt the flag.
An initial idea might be to use multivariate coppersmith since all the roots are very small, however this will(hopefully as it wasn't the intended solution) fail due to the degree of the polynomial and the many variables.

An important detail is that the maximum degree of a variable in any term of the polynomial is 2. This means that the monomial with the highest degree possible that may appear in it is $`v^2*w^2*x^2*y^2*z^2`$

The 5 unknowns are 239 bits so even the highest degree monomial will be approximately $`239*2*5 = 2390`$ bits.

Given that the modulus is roughly $`2*4*4096 = 32768`$ bits all the monomials are **extremely** small compared to it. This hints towards LLL which is in fact the solution.

The trick is to treat every monomial as its own variable, transforming the 5-variate polynomial of high degree to a 25-variate polynomial where every term is of degree only 1. This *linearizes* the equation making LLL a viable approach.

Another thing to take care of when constructing the basis matrix is to apply proper weighting to every column in order to make the target vector have elements all of approximately the same size. We can do that by scaling the columns in accordance with the degree of every monomial(i.e. the sum of the exponents of its variables) and the known size of the unknowns.
This is because we know the size of the unknowns is 239 bits so e.g. $`x^2`$ will have size $`2*239`$ bits and $`x^2*y*x`$ will, have size $`2*239 + 239 + 239 = 4*239`$ bits.

Relevant part of solver:
```python
# solve with LLL
lc = len(pol.coefficients())
coeffs = pol.coefficients()
exps = pol.exponents()
divsize = 2**(8*blocklen - 1)

M = matrix(QQ, lc + 1, lc + 1)
rescaling = [(divsize**sum(exps[i])) for i in range(lc)]


for i in range(lc):
    M[i, i] = 1/rescaling[i]
    M[i, lc] = coeffs[i]

M[lc, lc] = -n

B = M.LLL() # we expect the target vector to be in the reduced basis
```

Of course this will not actually recover the 5 parts of the key directly but only the values of the monomials. But we an do the rest with some applications of gcd, divisions and other simple manipulation of our values.
To recover the 5 values you can use groebner basis(recommended), hardcode what to gcd with what for the given polynomial in the `output.txt` or be silly like me and use sage's `solve()`
```python
def recover_XYZ(exps, vals):
    aa, bb, cc, dd, ee = var("aa, bb, cc, dd, ee")
    eqs = []
    for i in range(len(exps)):
        eqs.append(aa**exps[i][0] * bb**exps[i][1] * cc**exps[i][2] * dd**exps[i][3] * ee**exps[i][4] == vals[i])
    solution =  solve(eqs, [aa, bb, cc, dd, ee])
    if len(solution) == 0:
        print("no solutions found")
        return

    solution = [abs(int(str(i).split()[-1])) for i in solution[0]]
    return solution
  ```
  
In the end we can recover the key and decrypt the flag:
```
key = 'VxOriyvoRuqzPqq3RT6qRiLHzAlMZLJzcO47NDFp0Ub8qG9NGCGm74UuaZUBpswTzI1FxZsiHWLKBQFzLlTLnabORAHTER69pwLFaIMoqq9AcilGu3XCFQOCjDMhXyaXC9FVMUixFihUaLGhmukWcK'
b'crew{LLL1ne4r1z4ti0n_15_c0oLLL}\x01'
```
