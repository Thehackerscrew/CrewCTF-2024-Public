from Crypto.Util.number import getPrime, long_to_bytes, bytes_to_long
from hashlib import sha256
from Crypto.Cipher import AES

data = open("output.txt", "r").readlines()
exec(data[0])
exec(data[1])
exec(data[3])

K = Zmod(n)

PP.<v, w, x, y, z> = PolynomialRing(K)
exec(data[2].replace("^", "**"))


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

B = M.LLL()

def undo_rescaling(rescale_vec, vec):
    assert len(rescale_vec) == len(vec)
    newvec = [v*rv for v, rv in zip(vec, rescale_vec)]
    return newvec

for rrow in range(B.nrows()):
    crow = B.row(rrow)
    if crow[-1] == 0:
        rescaled = undo_rescaling(rescaling, crow[:-1])
        if rescaled[-1] == 0: continue
        rescaled =  [r*rescaled[-1] for r in rescaled]
        if rescaled[-1] == 1:
#            print(rescaled)
            break

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

def find_solution(exps, found_vector):
    my_exps = exps[:-1][::-1]
    my_exps = [list(ee) for ee in my_exps]
    my_vals = found_vector[:-1][::-1]
    sol = recover_XYZ(my_exps, my_vals)
    if sol == None:
        print()
        return
    myV, myW, myX, myY, myZ = sol
    key = "".join([int(part).to_bytes(blocklen, "big").decode() for part in [myV, myW, myX, myY, myZ]])
    print(f"{key = }")
    return key.encode()

key = find_solution(exps[-8:], rescaled[-8:])

if key != None:
    key = sha256(key).digest()
    print(AES.new(key, AES.MODE_ECB).decrypt(bytes.fromhex(c)))
else:
    print("failed :(")
