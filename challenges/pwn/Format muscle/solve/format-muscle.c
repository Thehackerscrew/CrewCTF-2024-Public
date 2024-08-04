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
