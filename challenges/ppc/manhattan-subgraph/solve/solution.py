from testcases import Edges
from hints import hints
import sys
sys.setrecursionlimit(1000000)

from Crypto.Hash import SHA1,SHA256

import itertools

N=40

def sha1digest(vis):
	h = SHA1.new()
	st=""
	for i in range(N):
		for j in range(N):
			for k in range(N):
				st+=str(int(vis[i][j][k]))
	h.update(st.encode())
	return h.digest()

def ins(x,y,z):
	if x<0 or x>=N or y<0 or y>=N or z<0 or z>=N:
		return False
	return True


Fans=open(f"answer.py","w")
Fans.write("solutions=[]\n")

for ((n,Edg),hint) in zip(Edges,hints):
	nei=[[] for i in range(n)]
	
	cnt=0
	for a in Edg:

		nei[a[0]].append((a[1],cnt))
		nei[a[1]].append((a[0],cnt+1))
		cnt+=2
	
	nei2=[[] for i in range(cnt)]
	for i in range(cnt):
		nei2[i].append((i^1,0))
	
	def add_cycle(arr):
		CYC=[]
		for i in range(4):
			CYC2=[arr[(i+j)%4] for j in range(4)]
			CYC.append(CYC2)
		CYC.sort()
		if CYC[0]!=arr:
			return
		for i in range(4):
			for j in range(4):
				if i!=j:
					if (i-j)%4==2:
						nei2[arr[i]].append((arr[j],0))
					else:
						nei2[arr[i]].append((arr[j],1))
	
	for i in range(n):
		for (a,idx1) in nei[i]:
			for (b,idx2) in nei[i]:
				if a!=b:
					for (c,idx3) in nei[a]:
						for (d,idx4) in nei[b]:
							if c==d and c!=i:
								add_cycle([idx1,idx2,idx4^1,idx3^1])
								add_cycle([idx1^1,idx2^1,idx4,idx3])
	
	Col=[-1 for i in range(cnt)]
	Vis=set({})
	ch=-1
	for a in nei2[0]:
		if a[1]==1:
			ch=a[0]
	Q=[0,ch]
	
	
	
	def DFS3(u):
		# ~ print(u)
		if u in Vis:
			return
		Vis.add(u)
		# ~ print(u)
		if type(u)==type(1):
			# ~ print(u,Col[u])
			#int
			# ~ print(u)
			for a in nei2[u]:
				if a[1]==0:
					assert(Col[a[0]]==Col[u] or Col[a[0]]==-1)
					Col[a[0]]=Col[u]
					# ~ print("ADD",a[0],Col[a[0]])
					DFS3(a[0])
				else:
					if Col[a[0]]!=-1:
						assert(Col[a[0]]!=Col[u])
						DFS3((u,a[0]))
		else:
			
			#pair
			(x,y)=u
			# ~ print("@",Col[x],Col[y])
			for a in nei2[x]:
				for b in nei2[y]:
					if a[1]==1 and b[1]==1 and a[0]==b[0]:
						# ~ print(x,y,a[0])
						Cl=3-Col[x]-Col[y]
						# ~ print(Cl,Col[a[0]],Col[x],Col[y])
						assert(Col[a[0]]==Cl or Col[a[0]]==-1)
						Col[a[0]]=Cl
						# ~ print(a[0])
						DFS3(a[0])
			None
	
	print("FIRST DFS")
	Col[0]=0
	DFS3(0)
	Col[ch]=1
	DFS3(ch)

	
	for a in Col:
		assert(a!=-1)
	
	nei3=[[] for i in range(cnt)]
	Col2=[-1 for i in range(cnt)]
	
	for i in range(n):
		for a in nei[i]:
			for b in nei[i]:
				if a!=b:
					if Col[a[1]]==Col[b[1]]:
						nei3[a[1]].append((b[1],1))
						nei3[b[1]].append((a[1],1))
	for i in range(cnt):
		nei3[i].append((i^1,1))
	
	for i in range(n):
		for (a,idx1) in nei[i]:
			for (b,idx2) in nei[i]:
				if a!=b:
					for (c,idx3) in nei[a]:
						for (d,idx4) in nei[b]:
							if c==d and c!=i:
								nei3[idx1].append((idx4,0))
								nei3[idx2].append((idx3,0))
	
	def DFS2(nd,cl=0):
		if Col2[nd]!=-1:
			assert(Col2[nd]==cl)
			return
		Col2[nd]=cl
		for a in nei3[nd]:
			DFS2(a[0],cl^a[1])
	
	print("SECOND DFS")
	for i in range(cnt):
		if Col2[i]==-1:
			# ~ print("NEW",Col[i])
			DFS2(i)
	
	
	
	pos=[-1 for i in range(n)]
	
	def DFS(place,cur=[0,0,0]):
		if pos[place]!=-1:
			assert(pos[place]==cur)
			return
		pos[place]=cur
		for a in nei[place]:
			Idx=Col[a[1]]
			Sign=2*Col2[a[1]]-1
			Idx=[int(i==PER[Idx])*BIN[Idx]*Sign for i in range(3)]
			DFS(a[0],[a+b for a,b in zip(cur,Idx)])
	
	print("FINAL DFS")
	SOLUTION=-1
	PER=[0,1,2]
	BIN=[1,1,1]
	pos=[-1 for i in range(n)]
	DFS(0)
	# ~ for a in pos:
		# ~ assert(a!=-1)
	Mn=[a for a in pos[0]]
	for a in pos:
		for i in range(3):
			Mn[i]=min(Mn[i],a[i])
	# ~ print(Mn)
	# ~ print(pos)
	for i in range(len(pos)):
		for j in range(3):
			pos[i][j]-=Mn[j]
	# ~ print(pos)
	S=dict({})
	for i in range(len(pos)):
		S[tuple(pos[i])]=i
	vis=[[[False for i in range(N)] for j in range(N)] for k in range(N)]
	for i in range(N):
		for j in range(N):
			for k in range(N):
				W=True
				Pts=[]
				for dx in range(0,2):
					for dy in range(0,2):
						for dz in range(0,2):
							if (i+dx,j+dy,k+dz) not in S:
								W=False
							else:
								Pts.append(S[(i+dx,j+dy,k+dz)])
				CNT=0
				for a in Pts:
					for b in nei[a]:
						if b[0] in Pts:
							CNT+=1
				if CNT==24:
					vis[i][j][k]=W
	
	
	
	for a in pos:
		FOUND=False
		for dx in range(-1,1):
			for dy in range(-1,1):
				for dz in range(-1,1):
					if ins(a[0]+dx,a[1]+dy,a[2]+dz):
						# ~ print(a[0]+dx,a[1]+dy,a[2]+dz)
						if vis[a[0]+dx][a[1]+dy][a[2]+dz]:
							FOUND=True
		
		assert(FOUND)
	
	
	
	for i in range(n):
		for a in nei[i]:
			
			diff=[pos[i][j]-pos[a[0]][j] for j in range(3)]
			assert(sum([abs(diff[j]) for j in range(3)])==1)
						
	print("BRUTEFORCE")
	NEXT=True
	while NEXT:
		NEXT=False
		for i in range(N):
			for j in range(N):
				for k in range(N):
					if vis[i][j][k]==False:
						POS=[i,j,k]
						ADD=True
						B=list(itertools.product(list([-1,1]),repeat=3))
						B2=list(itertools.product(list([0,1]),repeat=3))
						for BIN in B:
							for X in range(3):
								COR=False
								for delta in B2:
									# ~ print(delta)
									d=[delta[l]*BIN[l]*(1-int(l==X)) for l in range(3)]
									P=[a+b for (a,b) in zip(POS,d)]
									if ins(P[0],P[1],P[2]) and vis[P[0]][P[1]][P[2]]:
										COR=True
								if not COR:
									ADD=False
						if ADD:
							NEXT=True
							vis[i][j][k]=True
	# ~ print(vis)
	P = itertools.permutations([0,1,2])
	B=list(itertools.product(list([-1,1]),repeat=3))
	for PER in P:
		for BIN in B:
			vis2=[[[False for i in range(N)] for j in range(N)] for k in range(N)]
			for i in range(N):
				for j in range(N):
					for k in range(N):
						Q=[i,j,k]
						# ~ print(PER)
						# ~ print(Q)
						P2=[Q[PER[l]] for l in range(3)]
						for l in range(3):
							if BIN[l]==-1:
								P2[l]=N-1-P2[l]
						vis2[P2[0]][P2[1]][P2[2]]=vis[i][j][k]
			
			
			# ~ print("TEST",sha1digest(vis)==hint)
			if sha1digest(vis2)==hint:
				SOLUTION=vis2

	if SOLUTION!=-1:
		print("FOUND!")
	else:
		print("NOT FOUND!")
	Fans.write(f"solutions.append({SOLUTION})\n")
	# ~ exit(0)
	
Fans.close()
