import mpr121
import sons
import machine
import esp32
from machine import Pin, SoftI2C, SoftSPI, freq, ADC, Timer
import time
import gpio
from ad9833 import *

############# Main #####################################
#getMemory()
machine.freq(240000000)
#print("Frequence ESP32: ",machine.freq(),"hz")
temp_F = esp32.raw_temperature() - 32
print("internal temperature of the MCU en degres: ",temp_F *5/9)

################## Init MCP121 KBD ##############
i2c = SoftI2C(scl=Pin(22), sda=Pin(23), freq=1000000)

mpr121_A = mpr121.MPR121(i2c, address=0x5A)
mpr121_B = mpr121.MPR121(i2c, address=0x5B)
mpr121_C = mpr121.MPR121(i2c, address=0x5C)
mpr121_D = mpr121.MPR121(i2c, address=0x5D)

################ Init AD9833 VCOs ###############
spi = SoftSPI(baudrate=100000, polarity=1, phase=0, sck=Pin(5), miso=Pin(19), mosi=Pin(18))
sons.tab_gen = sons.initAd9833(spi) 

################Inits MCP23017 GPIOs IRQs #################
i2c = gpio.initI2c()
MCP1 = gpio.initMCP1(i2c)
MCP2 = gpio.initMCP2(i2c)

gpio.setEtatInitial(i2c)

pin_irq1 = Pin(21, Pin.IN, Pin.PULL_UP)
pin_irq1.irq(lambda p:gpio.check_irq1(i2c), Pin.IRQ_FALLING)

pin_irq2 = Pin(16, Pin.IN, Pin.PULL_UP)
pin_irq2.irq(lambda p:gpio.check_irq2(i2c), Pin.IRQ_FALLING)

print("MODE:",sons.mode)
print("OCTAVE n°", sons.octave_offset)

############### Init Pot Freq LFO ###############
gpio.adc_pin = machine.ADC(Pin(34, mode=Pin.IN))
gpio.adc_pin.atten(ADC.ATTN_11DB)	#Full range: 3.3v

timer_FreqLfo = Timer(0) # Between 0-3 for ESP32
timer_FreqLfo.init(mode=Timer.PERIODIC, period=100, callback=gpio.read_FreqLFO1)

############ Init timer automatic GATE #############
sons.pin_Gate = Pin(sons.pinGate, mode=Pin.OUT, value=0)

timer_gate = Timer(1) # Between 0-3 for ESP32
timer_gate.init(mode=Timer.PERIODIC, period=400, callback=sons.sendGate)

#sons.testVCOs(MODE_SINE, 1000, 100)

############# Test DAC ##################
dac1 = machine.DAC(25)

############# LOOP #########################
while True:
    
    #for i in range(255):
    #    dac1.write(i)
    
    sons.pollingKBD(mpr121_A, mpr121_B, mpr121_C, mpr121_D, dac1)
        
    time.sleep_ms(1)
