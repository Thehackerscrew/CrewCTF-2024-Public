

WIP

# Understanding

The following uses a base address of `0x00400000`

## Data

```c
struct connection {
    struct node* node;
    uint64_t distance;
};

struct node {
    uint64_t distance;
    uint64_t visited;
    void* instruction;
    uint64_t connection_count;
    int128_t store;
    struct connection connections[0];
};
```

The `.data` contains an array of `node`s. After each node are `connection_count` `connection`s. The following Binary Ninja script can be used to correctly set the types:

```python
data = bv.get_section_by_name(".data")
address = data.start
while address < data.end:
    node = bv.define_user_data_var(address, bv.types["node"])
    address += len(node)
    connections = bv.define_user_data_var(address, ArrayType.create(bv.types["connection"], node.value["connection_count"]))
    address += len(connections)
```

The `.rodata` section contains:

- `keys` (`0x00404040`) is an array of 1024 16-byte integers used to alter the inputted flag.
- `comparison` (`0x00404030`) is a 16-byte integer that should equal the flag after all alterations have occurred.

The `.bss` section contains:

- `flag` (`0x00426d40`) is a 16-byte space where the flag is inputted.
- `fpregs` (`0x00426d50`) is a `user_fpregs_struct` (see `sys/user.h`) used to store the results of `PTRACE_GETFPREGS` calls.

## Registers

- `r15` points to `keys`.
- `xmm2` is constantly zero.

## Code

### `do_ptrace` (`0x00401159`)

This function takes two parameters:

- `node` (`r14`) the node to apply.
- `data` (`xmm1`) the data to apply the node to.

```assembly
00401159  0f10c1             movups  xmm0, xmm1
0040115c  498b5e10           mov     rbx, qword [r14+0x10 {node::instruction}]
```

It starts by setting `xmm0` to `xmm1` (`data`) and `rbx` to `[r14+10]` (`node->instruction`).

```assembly
00401160  b839000000         mov     eax, 0x39  ; fork
00401165  0f05               syscall 
00401167  4885c0             test    rax, rax
0040116a  0f84da000000       je      0x40124a
```

Next it does a `fork` system call and the execution diverges based on if the process is the child (`rax == 0`) or the parent.

#### Child

```assembly
0040124a  b865000000         mov     eax, 0x65  ; ptrace
0040124f  bf00000000         mov     edi, 0x0  ; PTRACE_TRACEME
00401254  be00000000         mov     esi, 0x0
00401259  ba00000000         mov     edx, 0x0
0040125e  41ba00000000       mov     r10d, 0x0
00401264  0f05               syscall 
```

The child side of the fork starts by performing a `ptrace` system call with the `PTRACE_TRACEME` request. This marks that the process is to be traced by the parent.

```assembly
00401266  b827000000         mov     eax, 0x27  ; getpid
0040126b  0f05               syscall 
0040126d  4989c4             mov     r12, rax
00401270  b83e000000         mov     eax, 0x3e  ; kill
00401275  4c89e7             mov     rdi, r12
00401278  be05000000         mov     esi, 0x5  ; SIGTRAP
```

Next the child does a `getpid` system call to get its PID, followed by a `kill` system call with that PID and `SIGTRAP`. This causes the process to yield execution to its tracer (the parent)

```assembly
0040127f  ffd3               call    rbx
```

After that, `rbx` (`node->instruction`) is called. Where execution ends up will vary based on the node.

```assembly
0040222a  66410ffd87e03700…  paddw   xmm0, xmmword [r15+0x37e0]
```

As an example, the initial node's instruction performs a packed word add on `xmm0` (`data`) and a value offset from `r15` (`keys`), storing the result is stored in `xmm0`.  All node instructions follow a similar pattern, but with different SSE instructions.

#### Parent

```assembly
00401170  4889c3             mov     rbx, rax
00401173  b83d000000         mov     eax, 0x3d  ; wait4
00401178  4889df             mov     rdi, rbx
0040117b  be00000000         mov     esi, 0x0
00401180  ba00000000         mov     edx, 0x0
00401185  41ba00000000       mov     r10d, 0x0
0040118b  0f05               syscall 
```

The parent side of the fork starts by performing a `wait4` system call with the PID of the child. This suspends execution until the child's `SIGTRAP`, at which point the parent has full control over the child.

```assembly
0040118d  b865000000         mov     eax, 0x65  ; ptrace
00401192  bf09000000         mov     edi, 0x9  ; PTRACE_SINGLESTEP
00401197  4889de             mov     rsi, rbx
0040119a  ba00000000         mov     edx, 0x0
0040119f  41ba00000000       mov     r10d, 0x0
004011a5  0f05               syscall 
004011a7  b83d000000         mov     eax, 0x3d  ; wait4
004011ac  4889df             mov     rdi, rbx
004011af  be00000000         mov     esi, 0x0
004011b4  ba00000000         mov     edx, 0x0
004011b9  41ba00000000       mov     r10d, 0x0
004011bf  0f05               syscall 
004011c1  b865000000         mov     eax, 0x65  ; ptrace
004011c6  bf09000000         mov     edi, 0x9  ; PTRACE_SINGLESTEP
004011cb  4889de             mov     rsi, rbx
004011ce  ba00000000         mov     edx, 0x0
004011d3  41ba00000000       mov     r10d, 0x0
004011d9  0f05               syscall 
004011db  b83d000000         mov     eax, 0x3d  ; wait4
004011e0  4889df             mov     rdi, rbx
004011e3  be00000000         mov     esi, 0x0
004011e8  ba00000000         mov     edx, 0x0
004011ed  41ba00000000       mov     r10d, 0x0
004011f3  0f05               syscall 
```

Next are two lots of:

- `ptrace` system call with the  `PTRACE_SINGLESTEP` action and the child's PID.
- `wait4` system call with the child's PID.

This causes the child to execute two instructions (the call and node instruction), before execution is again yielded to the parent.

```assembly
004011f5  b865000000         mov     eax, 0x65  ; ptrace
004011fa  bf0e000000         mov     edi, 0xe  ; PTRACE_GETFPREGS
004011ff  4889de             mov     rsi, rbx
00401202  ba00000000         mov     edx, 0x0
00401207  49ba506d42000000…  mov     r10, fpregs
00401211  0f05               syscall 
```

After that there is a `ptrace` system call with the `PTRACE_GETFPREGS` action, the child's PID and the address of `fpregs`. This results in the child's floating point registers being copied to `fpregs`.

```assembly
00401213  0f100425f06d4200   movups  xmm0, xmmword [fpregs.xmm_space]
0040121b  410f114620         movups  xmmword [r14+0x20 {node::store}], xmm0
```

Next, `[fpregs.xmm_space]` (the child's `xmm0` register / the modified `data`) is moved to `[r14 + 0x20]` (`node->store`).

```assembly
00401220  b83e000000         mov     eax, 0x3e  ; kill
00401225  4889df             mov     rdi, rbx
00401228  be09000000         mov     esi, 0x9  ; SIGKILL
0040122d  0f05               syscall 
0040122f  b83d000000         mov     eax, 0x3d  ; wait4
00401234  4889df             mov     rdi, rbx
00401237  be00000000         mov     esi, 0x0
0040123c  ba00000000         mov     edx, 0x0
00401241  41ba00000000       mov     r10d, 0x0
00401247  0f05               syscall 
00401249  c3                 retn     {__return_addr}
```

Finally:

- The `kill` system call is invoked with the `SIGKILL` signal and the child's PID.
- The `wair4` system call is invoked with the child's PID.
- The function returns.

This has the effect of killing the child and waiting for it to die, before returning.

#### Summary

In summary, `to_ptrace`:

- Takes `node` (`node *`) and `data` (`uint128_t`) arguments.
- Applies `node->instruction` to `data`.
- Stores the result in `node->store`.

