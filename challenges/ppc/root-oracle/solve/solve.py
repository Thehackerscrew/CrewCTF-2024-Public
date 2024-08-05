from pwn import *
import random
io=process(["python3","chal.py"])

def send_triple(a,b,c):
	io.sendline(f"{a},{b},{c}".encode())
	io.recvuntil(b"=")
	return int(io.recvline().decode())

def solve_level():
	io.recvuntil(b"===============")
	io.recvuntil(b"===============")
	io.recvuntil(b"=")
	n=int(io.recvline().decode())
	print(n)
	S=set(range(0,n))
	while len(S)>1:
		a=random.choice(list(S))
		S2=set({})
		for b in S:
			resp=send_triple(a,b,a)
			if resp==0:
				S2.add(b)
		if len(S2)<len(S):
			S=S2
	one=-1
	for a in S:
		one=a
	invper=[-1]*(n+1)
	invper[1]=one
	
	mx=1
	while mx<n:
		S=set({})
		for i in range(n):
			# ~ print(send_triple(invper[mx],i,invper[mx]))
			if send_triple(invper[mx],i,invper[mx])<2 and i not in invper:
				S.add(i)
		# ~ if mx==1:
			# ~ invper[2]=list(S)[0]
			# ~ mx*=2
			# ~ continue
		for a in S:
			lo=0
			hi=mx
			while hi-lo>1:
				mid=(hi+lo)//2
				u=send_triple(invper[mid],a,invper[mid])
				if u==2:
					lo=mid
				else:
					hi=mid
			par=send_triple(invper[hi],a,invper[hi])
			if par==1:
				invper[2*hi]=a
			else:
				invper[2*hi-1]=a
		mx*=2
		# ~ print(mx,invper)
	per=[-1]*n
	for i in range(1,n+1):
		per[invper[i]]=i
	print(per)
	io.sendline(b"-1,-1,-1")
	io.sendline((",".join([str(a) for a in per])).encode())


for i in range(10):
	solve_level()

io.interactive()
