from sage.all import *

def cvp(B, t):
    t = vector(ZZ, t)
    B = B.LLL()
    S = B[-1].norm().round()+1
    L = block_matrix([
        [B,         0],
        [matrix(t), S]
    ])
    for v in L.LLL():
        if abs(v[-1]) == S:
            return t - v[:-1]*sign(v[-1])
    raise ValueError('cvp failed?!')

set_random_seed(1337)
p = 18315300953692143461
Fp = GF((p, 3))
a, b = Fp.random_element(), Fp.random_element()
I = Fp.gen()

def embed(M):
    M = matrix(M)
    R = zero_matrix(ZZ, M.nrows(), 3*M.ncols())
    R[:, 0::3] = M.apply_map(lambda z: z[0])
    R[:, 1::3] = M.apply_map(lambda z: z[1])
    R[:, 2::3] = M.apply_map(lambda z: z[2])
    return R

def unembed_vec(v):
    return vector([v[i] + v[i+1]*I + v[i+2]*I**2 for i in range(0, len(v), 3)])

leak = [50, 32, 83, 12, 49, 34, 81, 101, 46, 108, 106, 57, 105, 115, 102, 51, 67, 34, 124, 15, 125, 117, 51, 124, 38, 10, 30, 76, 125, 27, 89, 14, 50, 93, 88, 56]
n = len(leak)//3

As = matrix(Fp, [[a**i for i in range(n)]])
L = embed(As.stack(As*I).stack(As*I**2))
L = L.stack((identity_matrix(3*n)*p)[3:])

# constant term of the ith LCG output
B_ZZ = vector(embed([b*(a**i-1)/(a-1) for i in range(n)]))

trunc = 57
lb = vector([x<<trunc for x in leak]) - B_ZZ
ub = vector([(x+1)<<trunc for x in leak]) - B_ZZ
mid = (lb + ub) / 2
seq = unembed_vec(cvp(L, mid) + B_ZZ)

s = (seq[0]-b)/a
print(b'crew{' + bytes(s.to_integer().digits(256)[::-1]) + b'}')