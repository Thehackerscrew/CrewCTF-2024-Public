release_clean: release clean

release:
	python3 process.py
	nasm -f elf64 main.asm
	ld -s -o main main.o

clean:
	rm main.o text.asm data.asm rodata.asm
