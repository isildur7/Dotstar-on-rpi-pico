# Dotstar library for RPi Pico
# Amey Chaware
# March 2021

import machine
import array

class DotstarMatrix:
    """
    Object to control an Adafruit Dotstar LED Matrix.
    Multiple patterns and spiral indexing is available.
    """
    def __init__(self, brightness):
        """
        Initializer for the class, needs only global brightness.
        Assumes that we are using one 8x8 Dotstar matrix and currently
        simply use SPI0 for comms. Code for APA102-2020B LED units.
        
        Arguments -
        brightness  :  integer from 0 to 31
        """
        # 8x8 matrix
        self.numLED = 64
        
        #initialize SPI
        spi_sck=machine.Pin(2)
        spi_tx=machine.Pin(3)
        spi_rx=machine.Pin(4)
        self.spi=machine.SPI(0,baudrate=100000, sck=spi_sck, mosi=spi_tx, miso=spi_rx)
        
        #initialize brightness
        if int(brightness) > 31:
            print("brightness input out of bounds, set to highest value\n")
            self.brightness = 31
        elif int(brightness) < 0:
            print("brightness input out of bounds, set to zero\n")
            self.brightness = 0
        else:
            self.brightness = int(brightness)
        
        #  APA102 command structure:
        #  increasing time ---->>
        #              | byte 3 | byte 2 | byte 1 | byte 0 |
        #              |7      0|7      0|7      0|7      0|
        #              -------------------------------------
        #  Pixel       |111bbbbb|BBBBBBBB|GGGGGGGG|RRRRRRRR|
        #  Start Frame |00000000|00000000|00000000|00000000|
        #  Stop Frame  |11111111|11111111|11111111|11111111|
        
        # array to store the LED data, for all practical purposes this is the matrix.
        # initialize the matrix to have zero color values everywhere
        # global brightness is however set at this point
        # Why this works? I don't know but take a peek at SPIdotstar.py
        # each element of the array is an unsigned long - 32 bits
        self.led_ar = array.array("L", [(0xe0 | self.brightness) for _ in range(self.numLED+2)])
        #set start and end frames
        self.led_ar[0] = 0x0
        self.led_ar[-1] = 0xFFFFFFFF
        
        # Look up table for spiral pattern
        self.spiral = [37, 29, 28, 36, 44, 45, 46, 38, 30, 22, 21, 20, 19, 27, 35, 43, 51, 52, 53, 54, 55, 47, 39, 31, 23, 15, 14, 13, 12, 11, 10, 18, 26, 34, 42, 50, 58, 59, 60, 61, 62, 63, 64, 56, 48, 40, 32, 24, 16, 8, 7, 6, 5, 4, 3, 2, 1, 9, 17, 25, 33, 41, 49, 57]

    def __set_pattern(self):
        """
        private method, sends data from array to the actual matrix to set it
        """
        self.spi.write(bytearray(self.led_ar))
        return
    
    def __getitem__(self, key):
        """
        implementing [] operator access to LED array. self[key] will return
        color value of the LED number key as a hex code.
        """
        return hex((self.led_ar[key] >> 8) & 0xFFFFFF)
    
    def __setitem__(self, key, value):
        """
        implementing [] operator access to LED array. value is treated as a hex
        color code and LED number key is set to that color value.
        """
        self.led_ar[key] = int(value) << 8 | (0xe0 | self.brightness)
        self.__set_pattern()
        return
    
    def getSpiralIndex(self, key):
        """
        Fetch the LED color value at location key in the spiral pattern
        """
        return hex((self.led_ar[self.spiral[key]] >> 8) & 0xFFFFFF)
    
    def setSpiralIndex(self, key, value):
        """
        Set the LED color value at location key in the spiral pattern to the given
        hex code
        """
        self.led_ar[self.spiral[key]] = int(value) << 8 | (0xe0 | self.brightness)
        self.__set_pattern()
        return
    
    def fill(self, color):
        """
        Set all the LEDs to given hex color
        """
        for i in range(1, 1+self.numLED):
            self.led_ar[i] = int(color) << 8 | (0xe0 | self.brightness)
        
        self.__set_pattern()
        return
    
    def allOff(self):
        """
        turn all LEDs off
        """
        for i in range(1, 1+self.numLED):
            self.led_ar[i] = 0x0 << 8 | (0xe0 | self.brightness)
        
        self.__set_pattern()
        return
    
    def fillCircle(self, radius, color):
        """
        Fill up a 'circle' of LEDs (it fills up a square lol) of a given
        radius. Radius is not given in a distance metric, but rather as
        how many unique rings are inside the circle. So, for the 8x8 LED
        array, the radius is from 0 to 3 with 3 filling up the entire array.
        Arguments:
        radius           : Radius from 0 to 3
        color            : should be colour you want for the LED as either an int-hex.
        Returns:
        None
        """
        # number of LEDs 
        LED_in_radius = [4, 16, 36, 64]
        for i in range(LED_in_radius[radius]):
            self.led_ar[self.spiral[i]] = int(color) << 8 | (0xe0 | self.brightness)
        self.__set_pattern()
        return
    
    def ring(self, radius, color):
        """
        Fill up a ring of LEDs (it fills up a square ring lol) of a given
        radius. Radius is not given in a distance metric, but rather as
        how many unique rings are inside the circle. So, for the 8x8 LED
        array, the radius is from 0 to 3 with 3 turning on the outermost ring.
        Arguments:
        radius           : Radius from 0 to 3
        color            : should be colour you want for the LED as either an int-hex or rgb.
        Returns:
        None
        """
        LED_in_radius = [0, 4, 16, 36, 64]
        for i in range(LED_in_radius[radius], LED_in_radius[radius+1]):
            self.led_ar[self.spiral[i]] = int(color) << 8 | (0xe0 | self.brightness)
        self.__set_pattern()
        return
    
    def fillHalf(self, color, side):
        """
        turn on half of the array with given color
        Arguments:
        color       : should be colour you want for the LED as either an int-hex or rgb.
        side        : string, 't','b','r','l' for the top/bottom/right/left respectively
        Returns:
        None
        """
        if side == 'l':
            for i in range(32):
                self.led_ar[i+1] = int(color) << 8 | (0xe0 | self.brightness)
        
        elif side == 'r':
            for i in range(32):
                self.led_ar[i+33] = int(color) << 8 | (0xe0 | self.brightness)
        
        elif side == 't':
            for i in range(4):
                for j in range(i,57+i,8):
                    self.led_ar[j+1] = int(color) << 8 | (0xe0 | self.brightness)
        
        elif side == 'b':
            for i in range(4):
                for j in range(i,57+i,8):
                    self.led_ar[j+5] = int(color) << 8 | (0xe0 | self.brightness)      

        else:
            raise IOError("wrong side parameter, choose either 'l','r','t','b'")
        
        self.__set_pattern()
        return
    
    def fill24(self, color, side):
        """
        turn on 24 leds (3 rows) of the array with given color
        Arguments:
        color       : should be colour you want for the LED as either an int-hex or rgb.
        side        : string, 't','b','r','l' for the top/bottom/right/left respectively
        Returns:
        None
        """
        if side == 'l':
            for i in range(24):
                self.led_ar[i+1] = int(color) << 8 | (0xe0 | self.brightness)
        
        elif side == 'r':
            for i in range(24):
                self.led_ar[i+41] = int(color) << 8 | (0xe0 | self.brightness)
        
        elif side == 't':
            for i in range(3):
                for j in range(i,57+i,8):
                    self.led_ar[j+1] = int(color) << 8 | (0xe0 | self.brightness)
        
        elif side == 'b':
            for i in range(3):
                for j in range(i,57+i,8):
                    self.led_ar[j+6] = int(color) << 8 | (0xe0 | self.brightness)      

        else:
            raise IOError("wrong side parameter, choose either 'l','r','t','b'")
        
        self.__set_pattern()
        return
    
        