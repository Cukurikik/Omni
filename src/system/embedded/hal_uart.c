#include <stdint.h>

#define UART0_BASE 0x4000C000
#define UART_DR    (*((volatile uint32_t *)(UART0_BASE + 0x000)))
#define UART_FR    (*((volatile uint32_t *)(UART0_BASE + 0x018)))

#define TXFF (1 << 5)
#define RXFE (1 << 4)

void omni_uart_send(uint8_t data) {
    while (UART_FR & TXFF);
    UART_DR = data;
}

uint8_t omni_uart_receive(void) {
    while (UART_FR & RXFE);
    return (uint8_t)(UART_DR & 0xFF);
}
