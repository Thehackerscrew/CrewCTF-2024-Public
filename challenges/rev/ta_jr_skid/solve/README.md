

Community writeups:

- https://discord.com/channels/959047109015904306/1268933477575819316/1270856012139597834 (invite: https://discord.gg/rW3dj7GhDq)

# Understanding

The following uses a base address of `0x00400000`. You may also benefit from reading the source assembly (it is fairly well commented) and generation script.

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

And:

- Applies `node->instruction` to `data`.
- Stores the result in `node->store`.

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

### `_start` (`0x00401000`)

```assembly
00401000  b801000000         mov     eax, 0x1  ; write
00401005  bf01000000         mov     edi, 0x1  ; STDOUT
0040100a  48be004040000000…  mov     rsi, data_404000  {"Enter the flag: Correct!\nIncorr…"}
00401014  ba10000000         mov     edx, 0x10
00401019  0f05               syscall 
```

The program starts with a `write` system call to `STDOUT` asking the user to `Enter the flag:`.

```assembly
0040101b  b800000000         mov     eax, 0x0
00401020  bf00000000         mov     edi, 0x0
00401025  48be406d42000000…  mov     rsi, flag
0040102f  ba10000000         mov     edx, 0x10
00401034  0f05               syscall 
```

Then there is a `read` system call, taking 16 bytes of data from `STDIN` and storing them at `flag`.

```assembly
00401036  49bf404040000000…  mov     r15, keys
00401040  660fefd2           pxor    xmm2, xmm2
```

Next we have some setup:

- `r15` is set to `keys`, which is the start an array of 2048 16-byte integers.
- `xmm2` is zeroed.

```assembly
00401044  49be002742000000…  mov     r14, data_422700
0040104e  0f100c25406d4200   movups  xmm1, xmmword [flag]
00401056  e8fe000000         call    do_ptrace
```

Following that, we have some preparation:

- `r14` is set to `data_422700`, which is the initial `node`.
- `xmm1` is set to the contents of `flag`. Since `xmm1` is a 16-byte register, this is the entire input.

And `do_ptrace` is called, resulting in the initial `node`'s `instruction` being applied to the flag, with the result being stored in its `store`.

#### Outer Loop

This is the main loop that does the majority of the program's processing. It uses [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) find the shortest path between the initial `node` and final `node`, altering the `flag` as it goes.

##### Best Node Loop

This loop finds the best (shortest distance) unvisited `node`

```assembly
0040105b  41ba00040000       mov     r10d, 0x400
00401061  49bb409040000000…  mov     r11, data_409040
0040106b  41bc00000000       mov     r12d, 0x0
00401071  49c7c5ffffffff     mov     r13, 0xffffffffffffffff
```

It starts with some setup:

- `r10` is set to 1024, which is the number of nodes. It will be used to control when the loop exits.
- `r11` is set to `data_409040`, which the start of the array of `node`s. It will be used for the current node.
- `r12` is set to 0. It will be used to store the best `node`.
- `r13` is set to the maximum value. It will be used to store the best (smallest) distance.

```assembly
00401078  498b4308           mov     rax, qword [r11+0x8 {node::visited}]
0040107c  4885c0             test    rax, rax
0040107f  750e               jne     0x40108f
```

Next, it checks if the current `node` has been `visited`, branching if so (the branch destination will be covered later). At the start of execution, no `node`s have `visited` set.

```assembly
00401081  498b03             mov     rax, qword [r11 {node::distance}]
00401084  4939c5             cmp     r13, rax
00401087  7606               jbe     0x40108f
```

Then it checks if the current `node`'s `distance` is greater or equal to `r13` (the best distance), branching if so (again, the branch destination will be covered later). It is important to note that at the start of execution, the initial `node` has a 0 `distance`, whilst all other `node`s have a maximum distance.

```assembly
00401089  4d89dc             mov     r12, r11
0040108c  4989c5             mov     r13, rax
```

Next, assuming the two previous checks passed, `r12` (the best `node`) is set to the current node and `r13` (the best distance) is set to the current `node`'s distance.

```assembly
0040108f  498b4318           mov     rax, qword [r11+0x18 {node::connection_count}]
00401093  4801c0             add     rax, rax
00401096  4d8d5cc330         lea     r11, [r11+rax*8+0x30]
0040109b  49ffca             dec     r10
0040109e  75d8               jne     0x401078
```

After that is the branch destination. It uses the current `node`'s `connection_count` to advance `r11` to the next node, before decrementing `r10` (the loop exit control) and returning back to the start of the loop (after the setup) if it is non-zero.

##### Final Node Check

At this point:

- `r12` is the best `node`.
- `r13` is the best `node`'s distance.

```assembly
004010a0  410f104c2420       movups  xmm1, xmmword [r12+0x20 {node::store}]
004010a6  49c7442408010000…  mov     qword [r12+0x8 {node::visited}], 0x1
004010af  410f11542420       movups  xmmword [r12+0x20 {node::store}], xmm2
```

Next:

- The best `node`'s `store` is moved into `xmm1`.
- The `best` node is set to `visited`.
- The best `node`'s `distance` is set to `xmm2` (0). This done to obfuscate the path that has got to this point.

```assembly
004010b5  48b890a440000000…  mov     rax, data_40a490
004010bf  4939c4             cmp     r12, rax
004010c2  7437               je      0x4010fb
```

Then the `best` node is compared to `data_40a490` (the final `node`). If they are equal, the outer loop is exited (the branch destination is covered later)

##### Process Connections Loop

This loop goes through all of the best `node`'s `connection`s and:

- Calculates the distance to the `connection`'s `node` (through the best `node`).
- If the distance is less than the `connections`'s `node`'s `distance`:
  - The `connections`'s `node`'s `distance` is updated.
  - `do_ptrace` is used to update `connections`'s `node`'s `store` using its `instruction` and  `xmm1` (the best `node`'s `store`).

```assembly
004010c4  4d8b542418         mov     r10, qword [r12+0x18 {node::connection_count}]
004010c9  4d8d5c2430         lea     r11, [r12+0x30]
```

It starts with some setup:

- `r10` is set to the best `node`'s `connection_count`. This is used to control when the loop exits.
- `r11` is set to the first `connection`. This is used for the current `connection`.

```assembly
004010ce  4152               push    r10 {var_8_1}
004010d0  4153               push    r11 {var_10_1}
```

Next, both `r10` and `r11` are pushed to the stack. This is so they are retained in case of system calls performed by `do_ptrace`.

```assembly
004010d2  4d8b33             mov     r14, qword [r11 {connection::node}]
004010d5  498b4308           mov     rax, qword [r11+0x8 {connection::distance}]
004010d9  4c01e8             add     rax, r13
004010dc  493906             cmp     qword [r14 {node::distance}], rax
004010df  7608               jbe     0x4010e9
```

Then the  `connections`'s `distance` is added to the best distance. This is compared to the `connections`'s `node`'s existing `distance`. The program branches if the new distance is greater or equal than the existing distance (the branch destination will be covered later).

```assembly
004010e1  498906             mov     qword [r14 {node::distance}], rax
004010e4  e870000000         call    do_ptrace
```

Now, assuming the previous check passed, the `connections`'s `node`'s `distance` is updated with the new distance and `do_ptrace` is used  to update `connections`'s `node`'s `store` using its `instruction` and  `xmm1` (the best `node`'s `store`).

```assembly
004010e9  415b               pop     r11 {var_10_1}
004010eb  415a               pop     r10 {var_8_1}
004010ed  4983c310           add     r11, 0x10
004010f1  49ffca             dec     r10
004010f4  75d8               jne     0x4010ce
```

After that is the branch destination. It pops `r11` (the current `connection`) and `r10` (the exit control). The current `connection` is then advanced and the exit control is decremented, returning back to the start of the loop (after the setup) if it is non-zero.

##### Loop Back

```assembly
004010f6  e960ffffff         jmp     0x40105b
```

At the end of the outer loop, the program loops back to the start.

#### Final Node Comparison

The final part of the program is a comparison between the final `node`'s `store` and `comparison`. If they are equal, the flag was correct, otherwise it was wrong.

```assembly
004010fb  660fef0c25304040…  pxor    xmm1, xmmword [comparison]
00401104  660f3817c9         ptest   xmm1, xmm1
00401109  7427               je      0x401132
```

`xmm1` (the final `node`'s `store`) is XORed with `comparison`. If the result is 0 (they are equal), the program branches.

```assembly
0040110b  b801000000         mov     eax, 0x1  ; write
00401110  bf01000000         mov     edi, 0x1  ; STDOUT
00401115  48be194040000000…  mov     rsi, data_404000[0x19]  ; "Incorrect :(\n"
0040111f  ba0d000000         mov     edx, 0xd
00401124  0f05               syscall 
00401126  b83c000000         mov     eax, 0x3c  ; exit
0040112b  bf01000000         mov     edi, 0x1
00401130  0f05               syscall 
```

If there was no branch (they were not equal), a `write` system call is used to write `Incorrect :(` to `STDOUT` and the `exit` system call is used to exit the program with code 1.

```assembly
00401132  b801000000         mov     eax, 0x1  ; write
00401137  bf01000000         mov     edi, 0x1  ; STDOUT
0040113c  48be104040000000…  mov     rsi, data_404000[0x10]  ; "Correct :)\n"
00401146  ba09000000         mov     edx, 0x9
0040114b  0f05               syscall 
0040114d  b83c000000         mov     eax, 0x3c  ; exit
00401152  bf00000000         mov     edi, 0x0
00401157  0f05               syscall 
```

If there a branch (they were equal), a `write` system call is used to write `Correct :)` to `STDOUT` and the `exit` system call is used to exit the program with code 0.

# Solving

Now that we understand how the program works, we just need to reverse the process to get the flag. Our high level plan will be:

- Extract the data structures from the program using Binary Ninja scripting.
- Compute the path between the initial and final `node`s.
- Go backwards along the path, applying the inverse of the `instruction`s.

## Extraction

We can adapt our previous script to dump all the `node`s, their `connection`s and the text assembly of their `instruction`s, as well as the `keys`:

```python
from pathlib import Path
import pickle

nodes = {}

data = bv.get_section_by_name(".data")
address = data.start

while address < data.end:
    start_address = address

    node = bv.define_user_data_var(address, bv.types["node"])
    address += len(node)

    connections = bv.define_user_data_var(address, ArrayType.create(bv.types["connection"], node.value["connection_count"]))
    address += len(connections)

    nodes[start_address] = node.value
    nodes[start_address]["instruction"] = bv.get_disassembly(nodes[start_address]["instruction"])
    nodes[start_address]["connections"] = connections.value

(Path(__file__).parent / "nodes.pickle").write_bytes(pickle.dumps(nodes))

keys = bv.get_symbol_by_raw_name("keys")
(Path(__file__).parent / "keys.data").write_bytes(bv.read(keys.address, len(bv.get_data_var_at(keys.address))))
```

## Solving

The full solve script can be found in `solve.py`.

```python
from pathlib import Path
import pickle
import re

from instructions import *

nodes = pickle.loads((Path(__file__).parent / "nodes.pickle").read_bytes())
keys = (Path(__file__).parent / "keys.data").read_bytes()

INITIAL_NODE = 0x422700
FINAL_NODE = 0x40a490
```

We'll start with some imports, loading the dumped data, and copying over the addresses of the initial and final `node`s.

```python
nodes[INITIAL_NODE]["path"] = (INITIAL_NODE,)

while True:
    best_distance = 0xffffffffffffffff
    best_node = None
    for node in nodes.keys():
        if not nodes[node]["visited"] and nodes[node]["distance"] < best_distance:
            best_distance = nodes[node]["distance"]
            best_node = node

    if best_node == FINAL_NODE:
        break

    nodes[best_node]["visited"] = 1

    for connection in nodes[best_node]["connections"]:
        if nodes[best_node]["distance"] + connection["distance"] < nodes[connection["node"]]["distance"]:
            nodes[connection["node"]]["distance"] = nodes[best_node]["distance"] + connection["distance"]
            nodes[connection["node"]]["path"] = nodes[best_node]["path"] + (connection["node"],)
```

Next, we'll use [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm) to find the best path between the initial and final `node`s (in the exact same way as the binary).

```python
def get_instruction(assembly: str) -> Instruction:
    match = re.match(r"(?P<instruction>[a-z]+) +xmm0, xmmword \[r15\+0x(?P<offset>[0-9a-f]+)\]", assembly)

    instruction_class = {
        "paddb": AddbInstruction,
        "paddw": AddwInstruction,
        "paddd": AdddInstruction,
        "paddq": AddqInstruction,
        "pshufb": ShufbInstruction,
        "psubb": SubbInstruction,
        "psubw": SubwInstruction,
        "psubd": SubdInstruction,
        "psubq": SubqInstruction,
        "pxor": XorInstruction,
    }[match.group("instruction")]

    offset = int(match.group("offset"), 16)

    return instruction_class(offset, keys[offset:offset+0x10])
```

Now we'll implement a function to convert an assembly string into a Python representation. The `Instruction` classes are from `instructions.py` and (for brevity) will not be covered here.

```python
COMPARISON = bytes.fromhex("3483db49e20ca85f8a253766f860d0df")

flag = COMPARISON
for node in nodes[FINAL_NODE]["path"][::-1]:
    instruction = get_instruction(nodes[node]["instruction"])
    flag = instruction.reverse(flag)

print(flag,decode())
```

Finally we'll use the final `node`'s path work our way back from the `comparison` (copied from the binary) to the `flag`.

Running the script we get the output:

```
crew{a6b4291e38}
```

