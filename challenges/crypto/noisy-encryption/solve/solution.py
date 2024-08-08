from pwn import *
import itertools
import random

def bitcount(x):
	return sum([int(y) for y in bin(x)[2:]])

batch=5
e=[1,2,4]
strat=[]
for E in e:
	D=dict({})
	for i in range(pow(8,batch)):
		# ~ print(i)
		L=[]
		U=bitcount(i+pow(8,batch)*E)
		for j in range(1,pow(2,batch)):
			
			V=bitcount(i-pow(j,3)+pow(8,batch)*E)
			L+=[(U-V)%2]
			# ~ print(U,V,(U-V)%2)
		L=tuple(L)
		# ~ print(L)
		if L in D:
			# ~ print("ERR",bin(i),bin(D[L]))
			D[L].append(i)
			# ~ assert(False)
		else:
			D[L]=[i]
	# ~ Dstrategy.append(D)
	# ~ print(D)
	cnt=[0 for i in range(100)]
	for a in D:
		# ~ print(a,len(D[a]))
		assert(len(D[a])<100)
		cnt[len(D[a])]+=1
	print(cnt)
	strat.append(D)

# ~ cnt=[0 for i in range(100)]
# ~ for a in D:
	# ~ print(a,len(D[a]))
	# ~ assert(len(D[a])<100)
	# ~ cnt[len(D[a])]+=1
# ~ print(cnt)

def getnum(x):
	return int(x.decode().split(" ")[-1])


io=process(["python3","handout2.py"])
Queries=0
def tr(x):
	global Queries
	Queries+=1
	io.readline()
	io.sendline(str(x).encode())
	out=getnum(io.readline())
	return out



def guess(x):
	io.readline()
	io.sendline(b"guess")
	io.sendline(str(x).encode())
	out=io.recvall().decode()
	print(out)



sig=getnum(io.readline())
# ~ print("A")
# ~ print(tr(-1),tr(-2))
LM=1024
Ncount=(tr(-1)+1)%2

U=['?']*LM
DONE=[False]*LM
# ~ U[0]=1
# ~ for i in range(1,(LM//3)):
	# ~ u=tr(-pow(2,i))
	# ~ if u==Ncount:
		# ~ U[3*i]=0

U[-1]=1

for i in range(LM-1,-1,-3):
	if U[i]==1 and i//3>=batch:
		L=[]
		for j in range(1,pow(2,batch)):
			L+=[(Ncount-tr(-pow(2,(i//3-batch))*j))%2]
		L=tuple(L)
		# ~ print(L)
		X=strat[0][L]
		nums=[a for a in X]
		ans=[]
		for I in range(batch*3):
			has=0
			for j in range(len(nums)):
				has|=(1<<(nums[j]%2))
				nums[j]//=2
			if has==1:
				ans+=[0]
			if has==2:
				ans+=[1]
			if has==3:
				ans+=["?"]
		
		cnt=0
		for k in range(3*(i//3-batch),3*(i//3)):
			if ans[cnt]!="?":
				# ~ print(ans[cnt],k)
				U[k]=ans[cnt]
			cnt+=1
	if i+1<len(U) and U[i+1]==1 and U[i]==0 and i//3>=batch:
		L=[]
		for j in range(1,pow(2,batch)):
			L+=[(Ncount-tr(-pow(2,(i//3-batch))*j))%2]
		L=tuple(L)
		# ~ print(L)
		X=strat[1][L]
		
		nums=[a for a in X]
		ans=[]
		for I in range(batch*3):
			has=0
			for j in range(len(nums)):
				has|=(1<<(nums[j]%2))
				nums[j]//=2
			if has==1:
				ans+=[0]
			if has==2:
				ans+=[1]
			if has==3:
				ans+=["?"]
		
		cnt=0
		for k in range(3*(i//3-batch),3*(i//3)):
			if ans[cnt]!="?":
				# ~ print(ans[cnt],k)
				U[k]=ans[cnt]
			cnt+=1
				
	if i+2<len(U) and U[i+2]==1 and U[i+1]==0 and U[i]==0 and i//3>=batch:
		L=[]
		for j in range(1,pow(2,batch)):
			L+=[(Ncount-tr(-pow(2,(i//3-batch))*j))%2]
		L=tuple(L)
		# ~ print(L)
		X=strat[2][L]
		nums=[a for a in X]
		ans=[]
		for I in range(batch*3):
			has=0
			for j in range(len(nums)):
				has|=(1<<(nums[j]%2))
				nums[j]//=2
			if has==1:
				ans+=[0]
			if has==2:
				ans+=[1]
			if has==3:
				ans+=["?"]
		
		cnt=0
		for k in range(3*(i//3-batch),3*(i//3)):
			if ans[cnt]!="?":
				# ~ print(ans[cnt],k)
				U[k]=ans[cnt]
			cnt+=1

print(U)
print("Queries so far:",Queries)

ans=0
for i in range(len(U)):
	if U[i]==1:
		ans+=pow(2,i)
guess(pow(sig,3,ans))
