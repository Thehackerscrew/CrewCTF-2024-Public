[BITS 64]
or eax, 0x100000 ;beq $zero,$zero,0x34
lea rdi, [rel win]
xor eax, eax
mov al,59
syscall

win:
db "/win",0

pad:
times 33 db 0

dd 0x3c0c6e69, 0x358c772f, 0x23bdfff8, 0xafac0000, 0x03a02025, 0x240213c1, 0x0000000c

;dli $t0, 0x6e69772f
;sub $sp,$sp,8
;sw $t0,($sp)
;move $a0,$sp
;dli $v0, 5057
;syscall
