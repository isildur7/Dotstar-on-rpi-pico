import machine
import array
import utime

# def reverseBits(n, no_of_bits):
#     result = 0
#     for i in range(no_of_bits):
#         result <<= 1
#         result |= n & 1
#         n >>= 1
#     return result

spi_sck=machine.Pin(2)
spi_tx=machine.Pin(3)
spi_rx=machine.Pin(4)

spi=machine.SPI(0,baudrate=100000, sck=spi_sck, mosi=spi_tx, miso=spi_rx)

NUM_LEDS = 64
#value from 0 to 31
BRIGHTNESS = 1

led_ar = array.array("L", [0 for _ in range(NUM_LEDS+2)])
#end marker
led_ar[-1] = 0xffffffff

for i in range(1, 1+NUM_LEDS):
    rgb = 0x0 #change colour here
    
    #check APA102-2020 docs, first three bits are markers, next bits are brightness
    #then follow BGR pattern. These values are reversed. (LSB->MSB)
   
    #led_ar[i] = ((0xe0 | reverseBits(BRIGHTNESS, 5)) << 24) | (reverseBits((rgb & 0xFF), 8) << 16) | (reverseBits((rgb >> 8 & 0xFF), 8) << 8) | (reverseBits((rgb >> 16 & 0xFF), 8))
    
    #for some reason, this works and not the one above although
    #it may seem wrong. There is something about the bytearray method
    #that makes this work and I hope it doesn't change
    led_ar[i] = rgb << 8 | (0xe0 | BRIGHTNESS)
    
pre_final = bytearray(led_ar)
print(pre_final)

spi.write(pre_final)
