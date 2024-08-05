#define F_CPU 8000000
#define BAUD 38400

#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/eeprom.h>
#include <avr/sleep.h>
#include <avr/pgmspace.h>
#include <util/crc16.h>
#include <util/setbaud.h>

#include "printf/printf.h"
#include "tiny-AES-c/aes.h"

// move all string constants to flash memory
#define puts(X) printf_(PSTR(X))
#define printf(X, ...) printf_(PSTR(X), __VA_ARGS__)
#define strcmp(A, B) strcmp_P(A, PSTR(B))
#define strtok(A, B) strtok_P(A, PSTR(B))
#define strcpy(A, B) strcpy_P(A, PSTR(B))

#define log_event(X) log_event_(PSTR(X))

// disable interrupts while accessing EEPROM to prevent concurrent modification
#define LOCK_EEPROM cli
#define UNLOCK_EEPROM sei

// 7 times is good enough for Bruce Schneier
#define SECURE_ERASE_ITERATIONS 7

static_assert(AES_KEYLEN == 16, "using AES-128");

static EEMEM struct {
  uint8_t flag[64];
  uint8_t key[AES_KEYLEN];
  uint8_t user_data[64];
  uint16_t crc;
} eeprom_data;

uint8_t flag_length = sizeof(eeprom_data.flag);
uint8_t key_length = sizeof(eeprom_data.key);

char audit_log[128] = "AUDIT LOG START\n";

static void print_audit_log() {
  printf("%s", audit_log);
}

static void log_event_(const char *event) {
  if(strlen_P(event) + strlen(audit_log) + 1 > sizeof(audit_log)) {
    strcpy(audit_log, "AUDIT LOG RESET\n");
  }
  
  strcat_P(audit_log, event);
}

static uint16_t calc_eeprom_checksum() {
  const uint8_t *ptr = (void *)&eeprom_data;
  
  uint16_t crc_calc = 0xffff;
  
  for(size_t i = 0; i < sizeof(eeprom_data)-2; i++) {
    crc_calc = _crc16_update(crc_calc, eeprom_read_byte(ptr + i));
  }
  
  return crc_calc;
}

static bool verify_eeprom_integrity() {
  uint16_t crc_calc;
  uint16_t crc_check;
  
  LOCK_EEPROM();
  
  crc_calc = calc_eeprom_checksum();
  crc_check = eeprom_read_word(&eeprom_data.crc);
  
  UNLOCK_EEPROM();
  
  return crc_calc == crc_check;
}

static void update_eeprom_checksum() {
  uint16_t crc_calc = calc_eeprom_checksum();
  eeprom_write_word(&eeprom_data.crc, crc_calc);
}

static void write_eeprom_data(char *user_data) {
  LOCK_EEPROM();
  
  eeprom_update_block(user_data, &eeprom_data.user_data, sizeof(eeprom_data.user_data));
  
  update_eeprom_checksum();
  
  UNLOCK_EEPROM();
}

static void secure_erase_eeprom(uint8_t erase_value) {
  char temp_buffer[sizeof(eeprom_data.user_data)];
  
  memset(temp_buffer, erase_value, sizeof(temp_buffer));
  
  for(int i = 0; i < SECURE_ERASE_ITERATIONS; i++) {
    if(!verify_eeprom_integrity()) {
      puts("HALT! EEPROM corruption detected!");
      exit(0);
    }
    
    write_eeprom_data(temp_buffer);
    
    if(!verify_eeprom_integrity()) {
      puts("HALT! EEPROM corruption detected!");
      exit(0);
    }
  }
}

static void encrypt_flag() {
  static struct AES_ctx aes;
  static uint8_t key_buffer[AES_KEYLEN];
  static uint8_t flag_buffer[64];
  
  // sanity check
  if(key_length > sizeof(key_buffer) || flag_length > sizeof(flag_buffer)) {
    exit(0);
  }
  
  eeprom_read_block(key_buffer, &eeprom_data.key, key_length);
  AES_init_ctx(&aes, key_buffer);
  
  eeprom_read_block(flag_buffer, &eeprom_data.flag, flag_length);
  
  int blocks = (flag_length + AES_BLOCKLEN - 1) / AES_BLOCKLEN;
  
  for(int i = 0; i < blocks; i++) {
    AES_ECB_encrypt(&aes, &flag_buffer[i * AES_BLOCKLEN]);
  }
  
  for(size_t i = 0; i < flag_length; i++) {
    printf("%02x", flag_buffer[i]);
  }
  
  puts("\n");
  
  // remove sensitive data from RAM
  memset(&aes, 0, sizeof(aes));
  memset(key_buffer, 0, sizeof(key_buffer));
  memset(flag_buffer, 0, sizeof(flag_buffer));
}

int main() {
  if(MCUSR != 1) {
    exit(0);
  }
  
  MCUSR = 1; // reset power-on flag
  
  // configure UART
  LINCR = (1 << LENA) | (1 << LCMD2) | (1 << LCMD1) | (1 << LCMD0);
  LINBRR = UBRR_VALUE;
  LINENIR = (1 << LENRXOK);
  
  update_eeprom_checksum();
  
  sei();
  
  puts("Welcome to FlagSafe v2.3\n");
  
  while(1) {
    if(!verify_eeprom_integrity()) {
      puts("HALT! EEPROM corruption detected!");
      exit(0);
    }
  }
  
  return 0;
}

ISR(LIN_TC_vect) {
  static char input_buffer[256] = ">";
  static uint8_t input_head = 1;
  static uint8_t input_tail = 1;
  
  uint8_t status = LINSIR;
  
  if(status & (1 << LRXOK)) { // character received
    char data = LINDAT;
    
    if(data == '\n') {
      input_buffer[input_head++] = 0;
      
      char *command = strtok(&input_buffer[input_tail], " ");
      char *parameter = strtok(0, " ");
      
      if(*command) {
        input_tail = input_head;
        
        if(!strcmp(command, "write_data")) {
          if(parameter) {
            log_event("write user data\n");
            write_eeprom_data(parameter);
          } else {
            puts("Missing parameter: user data\n");
          }
        } else if(!strcmp(command, "secure_erase")) {
          if(parameter) {
            log_event("secure erase\n");
            secure_erase_eeprom(atoi(parameter));
          } else {
            puts("Missing parameter: erase value\n");
          }
        } else if(!strcmp(command, "encrypt_flag")) {
          log_event("encrypt flag\n");
          encrypt_flag();
        } else if(!strcmp(command, "audit_log")) {
          print_audit_log();
        } else {
          printf("Unknown command: \"%s\"\n", command);
        }
      }
      
      input_buffer[0] = '>';
      input_head = 1;
      input_tail = 1;
    } else {
      input_buffer[input_head++] = data;
    }
  }
}

// helper function for printf lib, output to UART
void _putchar(char c) {
  LINDAT = c;
  
  while(!(LINSIR&(1 << LTXOK)));
}
