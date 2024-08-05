#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "asf.h"

void UDP_Handler() {
  asf_udp_handler();
}

void usb_cdc_rx_notify() {
  
}

static volatile bool cdc_is_connected;

bool usb_cdc_enable() {
  cdc_is_connected = true;

  return true;
}

void usb_cdc_disable() {
  cdc_is_connected = false;
}

const uint8_t xor_sequence[] = { 204, 82, 149, 44, 105, 166, 154, 5, 56, 192, 22, 13, 80, 138, 151, 184, 31, 187, 74, 221, 110, 138, 66, 229, 155, 37, 147, 238, 210, 159, 202, 121, 30, 124 };

static uint16_t expand(uint8_t in) {
  return (in & 1) | ((in & 2) << 1) | ((in & 4) << 2) | ((in & 8) << 3) | ((in & 16) << 4) | ((in & 32) << 5) | ((in & 64) << 6) | ((in & 128) << 7);
}

static void clock(uint16_t value, int delay_ms) {
  for(int i = 0; i < delay_ms / 2; i++) {
    delay_ms(1);
    PIOA->PIO_SODR = value;
    delay_ms(1);
    PIOA->PIO_CODR = value;
  }
}

#define puts(X) udi_cdc_write_buf(X, strlen(X))

int main(int argc, char *argv[]) {
  sysclk_init();
  
  pmc_enable_periph_clk(ID_PIOA);
  pmc_enable_periph_clk(ID_PIOB);
  pmc_enable_periph_clk(ID_ADC);
  
  adc_init(ADC, sysclk_get_cpu_hz(), 20000000, ADC_MR_STARTUP_SUT8);
  adc_configure_timing(ADC, 0, ADC_MR_SETTLING_AST9, 2);
  adc_enable_channel(ADC, 5);
  
  NVIC_SetPriorityGrouping(0);

  irq_initialize_vectors();
  
  wdt_disable(WDT);
  
  cpu_irq_enable();
  
  udc_start();
  
  PIOA->PIO_PER = 0xFFFF;
  PIOA->PIO_OER = 0xFFFF;
  PIOA->PIO_CODR = 0xFFFF;
  
  while(1) {
    if(cdc_is_connected) {
      delay_ms(1000);
      
      puts("Flaggy the flag printer says: ");
      
      uint16_t output = 0;
      uint8_t last_char = 0;
      
      for(size_t i = 0; i < sizeof(xor_sequence); i++) {
        output = expand(xor_sequence[i] ^ last_char);
        
        PIOA->PIO_CODR = ~(output | (output << 1));
        PIOA->PIO_SODR = output | (output << 1);
        
        clock(output, 500);
        
        adc_start(ADC);
        
        while(!(adc_get_status(ADC) & ADC_ISR_DRDY));
        
        last_char = adc_get_latest_value(ADC) >> 5;
        
        udi_cdc_putc(last_char);
      }
      
      udi_cdc_putc('\r');
      udi_cdc_putc('\n');
      
      char c = udi_cdc_getc();
      
      if(c == 'E') {
        cpu_irq_disable();
        flash_clear_gpnvm(1);
        rstc_start_software_reset(RSTC);
      }
    }
  }
}
