global _start

section .text

%macro read 2
    mov rax, 0x00
    mov rdi, 0  ; STDIN
    mov rsi, %1
    mov rdx, %2
    syscall
%endmacro

%macro write 2
    mov rax, 0x01
    mov rdi, 1  ; STDOUT
    mov rsi, %1
    mov rdx, %2
    syscall
%endmacro

%macro fork 0
    mov rax, 0x39
    syscall
%endmacro

%macro getpid 0
    mov rax, 0x27
    syscall
%endmacro

%macro exit 1
    mov rax, 0x3c
    mov rdi, %1
    syscall
%endmacro

%define SIGTRAP 5
%define SIGKILL 9
%macro kill 2
    mov rax, 0x3e
    mov rdi, %1
    mov rsi, %2
    syscall
%endmacro

%macro wait4 1
    mov rax, 0x3d
    mov rdi, %1
    mov rsi, 0
    mov rdx, 0
    mov r10, 0
    syscall
%endmacro

%define PTRACE_TRACEME 0
%define PTRACE_SINGLESTEP 9
%define PTRACE_GETFPREGS 14
%macro ptrace 4
    mov rax, 0x65
    mov rdi, %1
    mov rsi, %2
    mov rdx, %3
    mov r10, %4
    syscall
%endmacro

%macro waitid 1
    mov rax, 0xf7
    mov rdi, 1  ; P_PID
    mov rsi, %1
    mov rdx, 0
    mov r10, 0
    mov r8, 0
    syscall
%endmacro

_start:
    ; node + 0x00 - Distance
    ; node + 0x08 - Visited
    ; node + 0x10 - Instruction
    ; node + 0x18 - Connection count
    ; node + 0x20 - Store
    ; node + 0x30 + i * 8 - Connection node
    ; node + 0x38 + i * 8 - Connection distance

    write enter_flag_string, enter_flag_length
    read flag, 16

    mov r15, ig_memory  ; ig_memory
    pxor xmm2, xmm2  ; Zero

    ; Setting up the start node.
    mov r14, node_start
    movups xmm1, oword [flag]
    call do_ptrace

big_loop:
    mov r10, node_count  ; i
    mov r11, nodes  ; Current node
    mov r12, 0  ; Best node
    mov r13, 0xffffffffffffffff  ; Best distance

find_best_node_loop:
    mov rax, qword [r11 + 0x08]
    test rax, rax  ; Current visited
    jnz find_best_node_reject  ; Current visited !- 0
    mov rax, qword [r11 + 0x00]  ; Current distance
    cmp r13, rax
    jbe find_best_node_reject  ; Best distance <=u Current distance
    mov r12, r11  ; Best node = Current node
    mov r13, rax  ; Best distance = Current distance
    
find_best_node_reject:
    mov rax, qword [r11 + 0x18]  ; Current connection count
    add rax, rax  ; Make the scale factor work
    lea r11, [r11 + 0x30 + rax * 8]  ; Current node = Next node

    dec r10
    jnz find_best_node_loop  ; --i != 0

    ; r12 = Current node
    ; r13 - Current distance
    movups xmm1, oword [r12 + 0x20]  ; Current store

    mov qword [r12 + 0x08], 1  ; Current visited = 1
    movups oword [r12 + 0x20], xmm2 ; Zero store for good measure

    mov rax, node_end
    cmp r12, rax
    je at_last_node  ; Current node == End node

    mov r10, qword [r12 + 0x18]  ; i (Current connection count)
    lea r11, [r12 + 0x30]  ; Current connection

process_connections_loop:
    push r10  ; Keep accross system calls
    push r11  ; Keep accross system calls

    mov r14, qword [r11]  ; Next node
    mov rax, qword [r11 + 8]
    add rax, r13  ; New next distance
    cmp qword [r14], rax
    jbe process_connection_reject  ; Next distance <=u New next distance

    mov qword [r14], rax  ; Next distance = New next distance

    call do_ptrace

process_connection_reject:
    pop r11  ; Keep accross system calls
    pop r10  ; Keep accross system calls

    add r11, 0x10
    dec r10
    jnz process_connections_loop  ; i-- != 0

    jmp big_loop

at_last_node:
    pxor xmm1, oword [check]
    ptest xmm1, xmm1
    jz correct ; End node store == Check

    write incorrect_string, incorrect_length
    exit 1

correct:
    write correct_string, correct_length
    exit 0

do_ptrace:  ; r14 (Next node), xmm1 (Store)
    movups xmm0, xmm1  ; Store
    mov rbx, qword [r14 + 0x10]  ; Next instruction
    fork
    test rax, rax
    jz child

    mov rbx, rax  ; Child PID
    wait4 rbx
    ptrace PTRACE_SINGLESTEP, rbx, 0, 0  ; Step the "call rbx".
    wait4 rbx
    ptrace PTRACE_SINGLESTEP, rbx, 0, 0  ; Step the instruction.
    wait4 rbx
    ptrace PTRACE_GETFPREGS, rbx, 0, user_fpregs_struct
    movups xmm0, oword [user_fpregs_struct_xmm0]  ; Store
    movups oword [r14 + 0x20], xmm0  ; Next store = Store
    kill rbx, SIGKILL
    wait4 rbx

    ret

child:
    ptrace PTRACE_TRACEME, 0, 0, 0
    getpid
    mov r12, rax
    kill r12, SIGTRAP  ; Signal ourself so PTRACE can take control.
    call rbx

%include "text.asm"

section .data
%include "data.asm"

section .rodata
enter_flag_string:
    db 'Enter the flag: '
enter_flag_length equ $-enter_flag_string

correct_string:
    db 'Correct!', 10
correct_length equ $-correct_string

incorrect_string:
    db 'Incorrect :(', 10
incorrect_length equ $-incorrect_string

%include "rodata.asm"

section .bss
flag:
    resb 16
user_fpregs_struct:
    resb 160
user_fpregs_struct_xmm0:
    resb 352
