from pwn import *

n=100
m=100
tests=10

def genHash(V):
	Hash=[]
	for i in range(len(V)):
		Value=0
		for j in range(len(V)):
			if j==i and j>0:
				Value-=V[j-1]
				Value+=(V[j]^V[j-1])
			else:
				Value+=V[j]
		Hash.append(Value)
	return Hash

def solveInstance(Hsh):
	AND=[]
	sm=Hsh[0]
	for i in range(1,n):
		Nm=(sm-Hsh[i])//2
		Nm=bin(Nm)[2:]
		Nm=Nm.zfill(m)
		Nm=list([int(x) for x in Nm])
		Nm=Nm[::-1]
		AND.append(Nm)

	CNT=[[0 for i in range(n+1)] for j in range(m)]
	for j in range(m):
		DP=[[[0,0] for j in range(n+1)]  for i in range(n)]
		DP[0][0][0]=1
		DP[0][1][1]=1
		for pos in range(n-1):
			for cnt in range(n+1):
				for last in range(2):
					for nxt in range(2):
						if (last*nxt)==AND[pos][j] and cnt+nxt<=n:
							DP[pos+1][cnt+nxt][nxt]+=DP[pos][cnt][last]
		for k in range(n+1):
			CNT[j][k]=sum(DP[n-1][k])
	MX=2*n+10
	EXT=m+10
	DP=[0 for i in range(MX)]
	DP[0]=1
	TAR=sm
	TAR=bin(TAR)[2:]
	TAR=TAR.zfill(EXT)
	TAR=list([int(x) for x in TAR])
	TAR=TAR[::-1]
	for i in range(EXT):
		Nxt=[0 for i in range(len(DP))]
		for j in range(len(DP)):
			if DP[j]>0:
				if i<m:
					for k in range(n+1):
						Nxstate=(k+j-TAR[i])
						if Nxstate>=0 and Nxstate%2==0:
							Nxt[Nxstate//2]+=DP[j]*CNT[i][k]
				else:
					Nxstate=(j-TAR[i])
					if Nxstate>=0 and Nxstate%2==0:
						Nxt[Nxstate//2]+=DP[j]
		DP=Nxt
	print(DP[0])
	return DP[0]
		
io=process(["python3","server.py"])

io.recvline()
def solve():
	global n,m
	print(io.recvline())
	out=io.recvline().decode()
	Hsh=eval(out)
	Ans=solveInstance(Hsh)
	io.sendline(str(Ans).encode())
	print(io.recvline())

for T in range(tests):
	solve()
io.interactive()
