CFLAGS += -mmcu=atmega16m1 -O2 -Wall -Wextra -Werror -ffunction-sections -fdata-sections -Wl,-Map,main.map -Wl,--gc-sections
CFLAGS += -DPRINTF_DISABLE_SUPPORT_FLOAT -DPRINTF_DISABLE_SUPPORT_LONG_LONG -DPRINTF_DISABLE_SUPPORT_PTRDIFF_T
CFLAGS += -DCBC=0 -DCTR=0

SRCS := main.c printf/printf.c tiny-AES-c/aes.c
DEPS := printf/printf.h tiny-AES-c/aes.h

.PHONY: all sim

all: main.hex main.lss

main.hex: main.elf
	avr-objcopy -R .eeprom -O ihex $< $@

main.lss: main.elf
	avr-objdump -h -S $< > $@

main.elf: $(SRCS) $(DEPS) Makefile
	avr-gcc $(CFLAGS) $(SRCS) -o $@

sim: all
	./run_avr -m atmega16m1 -f 8000000 main.hex -ee eeprom.hex
