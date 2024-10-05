# register addresses in port=0, bank=1 mode (easier maths to convert)
_MCP_IODIRA        = const(0x00) # R/W I/O Direction Register
_MCP_IPOLA         = const(0x02) # R/W Input Polarity Port Register
_MCP_GPINTENA      = const(0x04) # R/W Interrupt-on-Change Pins
_MCP_DEFVALA       = const(0x06) # R/W Default Value Register
_MCP_INTCONA       = const(0x08) # R/W Interrupt-on-Change Control Register
_MCP_IOCONA        = const(0x0a) # R/W Configuration Register
_MCP_GPPUA         = const(0x0c) # R/W Pull-Up Resistor Register
_MCP_INTFA         = const(0x0e) # R   Interrupt Flag Register (read clears)
_MCP_INTCAPA       = const(0x10) # R   Interrupt Captured Value For Port Register
_MCP_GPIOA         = const(0x12) # R/W General Purpose I/O Port Register
_MCP_OLATA         = const(0x14) # R/W Output Latch Register

# register addresses in port=0, bank=0 mode 
_MCP_IODIRB        = const(0x01) # R/W I/O Direction Register
_MCP_IPOLB         = const(0x03) # R/W Input Polarity Port Register
_MCP_GPINTENB     = const(0x05) # R/W Interrupt-on-Change Pins
_MCP_DEFVALB       = const(0x07) # R/W Default Value Register
_MCP_INTCONB       = const(0x09) # R/W Interrupt-on-Change Control Register
_MCP_IOCONB        = const(0x0b) # R/W Configuration Register
_MCP_GPPUB         = const(0x0d) # R/W Pull-Up Resistor Register
_MCP_INTFB         = const(0x0f) # R   Interrupt Flag Register (read clears)
_MCP_INTCAPB       = const(0x11) # R   Interrupt Captured Value For Port Register
_MCP_GPIOB         = const(0x13) # R/W General Purpose I/O Port Register
_MCP_OLATB         = const(0x15) # R/W Output Latch Register

# Config register (IOCON) bits
_MCP_IOCON        = const(0x05) # R/W Configuration Register
_MCP_IOCON_INTPOL = const(2)
_MCP_IOCON_ODR    = const(4)
# _MCP_IOCON_HAEN = const(8) # no used - for spi flavour of this chip
_MCP_IOCON_DISSLW = const(16)
_MCP_IOCON_SEQOP  = const(32)
_MCP_IOCON_MIRROR = const(64)
_MCP_IOCON_BANK   = const(128)

_MCP1			  = const(0x20)
_MCP2			  = const(0x21)

import micropython
import machine
from machine import Pin, SoftI2C, ADC, SoftSPI, Timer
import mpr121
import sons
import math
from ad9833 import *


waveFormLFO1 = MODE_SINE
freqLFO1 = 0
old_freqLFO1 = 0.01

state = 0 # state IRQ

adc_pin = 0

OFF = const(3)

def affMode(mode):
    if mode==0:
        return "SINUS"
    elif mode==1:
        return "TRIANGLE"
    elif mode==2:
        return "CARRE"
    elif mode==3:
        return "OFF"
    else:
        return "MODE NON DEFINI"
    
#lire fréquence LFO
def read_FreqLFO1(p):
    global freqLFO1
    global adc_pin
    global old_freqLFO1
    global waveFormLFO1
    
    value = adc_pin.read()
    if (value<1000):        
        freqLFO1 = (math.floor(value / 100) / 10)
    else:
        freqLFO1 = math.floor(value / 30) - 32
    #print("Frequ: ",freqLFO1, "Old Freq: ", old_freqLFO1)
    #print("Value: ",value)
    #freqLFO1 = 0.5
    
    if ((freqLFO1 != old_freqLFO1) & (freqLFO1 != old_freqLFO1+1)  & (freqLFO1 != old_freqLFO1-1)):
        sons.sendLFO(freqLFO1, waveFormLFO1)
    #print(waveFormLFO1)
        
    old_freqLFO1 = freqLFO1
    #old_freqLFO1 = int(old_freqLFO1)
      
def setOctave(toctave):
    sons.octave_offset = toctave
    print("CONTACT OCTAVE n°", sons.octave_offset)

def setMode(tmode):
    sons.mode = tmode
    sons.resetTabNotes()
    print("CONTACT MODE:",tmode)
    
def bytes_to_int(value):
    return int.from_bytes(bytearray(value), 'little')
    
#reli un registre et l'affiche
def printRegister(i2c,addr, reg, nbBytes, name):
    print(name,hex(bytes_to_int(i2c.readfrom_mem(addr, reg, nbBytes))))

def initI2c():
    i2c = SoftI2C(scl=Pin(22), sda=Pin(23), freq=1000000)
    return i2c

#renvoyer adresses registres
def getMCP_GPIOA():
    return _MCP_GPIOA

def getMCP_GPIOB():
    return _MCP_GPIOB


def initMCP1(i2c):
    MCP = initMcp(i2c, _MCP1, 1)
    return MCP
    
def initMCP2(i2c):
    MCP = initMcp(i2c, _MCP2, 2)
    return MCP

    
def writeI2c(i2c, addr, reg, val):
    i2c.writeto_mem(addr, reg, bytearray([val]))

def initMcp(i2c, MCP, numMCP):
    if numMCP==2:
        value = 0x00
        mask = 0xff
    else:
        value = 0xf0
        mask = 0x0f
        
    #print("########## MCP num ", numMCP, "##########")
    #configurer le reg de config IOCON
    writeI2c(i2c, MCP,_MCP_IOCON, _MCP_IOCON_DISSLW | _MCP_IOCON_MIRROR | _MCP_IOCON_SEQOP)
    writeI2c(i2c, MCP,_MCP_IOCONA, _MCP_IOCON_DISSLW | _MCP_IOCON_MIRROR | _MCP_IOCON_SEQOP)
    writeI2c(i2c, MCP,_MCP_IOCONB, _MCP_IOCON_DISSLW | _MCP_IOCON_MIRROR | _MCP_IOCON_SEQOP)
    #printRegister(i2c, MCP, _MCP_IOCONB, 1,"_MCP_IOCON")

    #GPIO en entrée
    writeI2c(i2c, MCP, _MCP_IODIRA, 0xff)
    #printRegister(MCP, _MCP_IODIRA, 1,"_MCP_IODIRA")

    #Polarité
    writeI2c(i2c, MCP, _MCP_IPOLA, 0x00)
    #printRegister(MCP, _MCP_IPOLA, 1,"_MCP_IPOLA")

    #Pullup sur ports GPIO
    writeI2c(i2c, MCP, _MCP_GPPUA, 0xff)
    #printRegister(MCP, _MCP_GPPUA, 1,"_MCP_GPPUA")

    #Activer les IRQ
    writeI2c(i2c, MCP, _MCP_GPINTENA, mask)
    #printRegister(i2c, MCP, _MCP_GPINTENA, 1,"_MCP_GPINTENA")

    #4 bits poid fort sur Defval pour MPR121
    #4 bits poid faible sur compare avec val precedentes pour Contacteurs
    writeI2c(i2c, MCP, _MCP_DEFVALA, value)
    #printRegister(MCP, _MCP_DEFVALA, 1,"_MCP_DEFVALA")

    writeI2c(i2c, MCP, _MCP_INTCONA, value)
    #printRegister(MCP, _MCP_INTCONA, 1,"_MCP_INTCONA")

    #Lire reg INTCAP - INTF
    #printRegister(MCP, _MCP_INTCAPA, 1,"_MCP_INTCAPA")
    #printRegister(MCP, _MCP_INTFA, 1,"_MCP_INTFA")
    #print()

    ##################PORT B#########################
    #GPIO en entrée
    writeI2c(i2c, MCP, _MCP_IODIRB, 0xff)
    #printRegister(MCP, _MCP_IODIRB, 1,"_MCP_IODIRB")

    #Polarité
    writeI2c(i2c, MCP, _MCP_IPOLB, 0x00)
    #printRegister(MCP, _MCP_IPOLB, 1,"_MCP_IPOLB")

    #Pullup sur ports GPIO
    writeI2c(i2c, MCP, _MCP_GPPUB, 0xff)
    #printRegister(MCP, _MCP_GPPUB, 1,"_MCP_GPPUB")

    #Activer les IRQ
    writeI2c(i2c, MCP, _MCP_GPINTENB, 0xff)
    #printRegister(i2c,MCP, _MCP_GPINTENB, 1,"_MCP_GPINTENB")

    #Pas de DEFVAL
    writeI2c(i2c, MCP, _MCP_DEFVALB, 0x00)
    #printRegister(MCP, _MCP_DEFVALB, 1,"_MCP_DEFVALB")

    #8 bits sur compare avec val precedentes pour Contacteurs
    writeI2c(i2c, MCP, _MCP_INTCONB, 0x00)
    #printRegister(i2c, MCP, _MCP_INTCONB, 1,"_MCP_INTCONB")

    #Lire reg INTCAP - INTF
    #printRegister(MCP, _MCP_INTCAPB, 1,"_MCP_INTCAPB")
    #printRegister(MCP, _MCP_INTFB, 1,"_MCP_INTFB")
    #print()
    return MCP

#Lire etat GPIO MCP2
def readEtatInitial(i2c, MCP, GPIO):
    tMcp = i2c.readfrom_mem(MCP, GPIO, 1)
    #initialiser variables selon etat des entrees de MCP2
    tMcp = bytes_to_int(tMcp)
    return tMcp
    
def setEtatInitial(i2c):
    #lire adresses registres MCP etat initial   
    tMcp1A = readEtatInitial(i2c, _MCP1, _MCP_GPIOA)
    tMcp1B = readEtatInitial(i2c, _MCP1, _MCP_GPIOB)
    tMcp2A = readEtatInitial(i2c, _MCP2, _MCP_GPIOA)
    tMcp2B = readEtatInitial(i2c, _MCP2, _MCP_GPIOB)
    
    print("Etat initial GPIOs:")
    print("GPIO_1A:",hex(tMcp1A))
    print("GPIO_1B:",hex(tMcp1B))
    print("GPIO_2A:",hex(tMcp2A))
    print("GPIO_2B:",hex(tMcp1B))
    
    ######## GPIO 1 port A Octaves ####################
    if tMcp1A & 0x0f == 0x0e:
        setOctave(0)
    elif tMcp1A & 0x0f == 0x0d:
        setOctave(1)
    elif tMcp1A & 0x0f == 0x0b:
        setOctave(2)
    elif tMcp1A & 0x0f == 0x07:
        setOctave(3)
        
    ######## GPIO 1 port B Modes ####################
    if tMcp1B & 0x0f == 0x0e:
        sons.mode = sons.tabMode[0] #monophonique
    elif tMcp1B & 0x0f == 0x0d:
        sons.mode = sons.tabMode[1] #polyphonique
    elif tMcp1B & 0x0f == 0x0b:
        sons.mode = sons.tabMode[2] #sequenceur
    elif tMcp1B & 0x0f == 0x07:
        sons.mode = sons.tabMode[3] #Portamento

    ######### GPIO 1 port B Waveform LFO #############
    if tMcp1B & 0xf0 == 0xe0:
        sons.waveFormLFO1 = MODE_SINE
        sons.sendLFO(freqLFO1, MODE_SINE)
    elif tMcp1B & 0xf0 == 0xd0:
        sons.waveFormLFO1 = MODE_TRIANGLE
        sons.sendLFO(freqLFO1, MODE_SINE)
    elif tMcp1B & 0xf0 == 0xb0:
        sons.waveFormLFO1 = MODE_CLOCK
        sons.sendLFO(freqLFO1, MODE_SINE)
    elif tMcp1B & 0xf0 == 0x70:
        sons.waveFormLFO1 = OFF
        sons.sendLFO(freqLFO1, OFF)
        
    ######### GPIO 2 port A Waveform VCO 1 #############
    if tMcp2A & 0xf0 == 0xe0:
        sons.waveFormVCO1 = MODE_SINE
    elif tMcp2A & 0xf0 == 0xd0:
        sons.waveFormVCO1 = MODE_TRIANGLE
    elif tMcp2A & 0xf0 == 0xb0:
        sons.waveFormVCO1 = MODE_CLOCK
    elif tMcp2A & 0xf0 == 0x70:
        sons.waveFormVCO1 = OFF
        
    ######### GPIO 2 port A Waveform VCO 2 #############
    if tMcp2A & 0x0f == 0x0e:
        sons.waveFormVCO2 = MODE_SINE
    elif tMcp2A & 0x0f == 0x0d:
        sons.waveFormVCO2 = MODE_TRIANGLE
    elif tMcp2A & 0x0f == 0x0b:
        sons.waveFormVCO2 = MODE_CLOCK
    elif tMcp2A & 0x0f == 0x07:
        sons.waveFormVCO2 = OFF
        
    ######### GPIO 2 port B Waveform VCO 3 #############
    if tMcp2B & 0x0f == 0x0e:
        sons.waveFormVCO3 = MODE_SINE
    elif tMcp2B & 0x0f == 0x0d:
        sons.waveFormVCO3 = MODE_TRIANGLE
    elif tMcp2B & 0x0f == 0x0b:
        sons.waveFormVCO3 = MODE_CLOCK
    elif tMcp2B & 0x0f == 0x07:
        sons.waveFormVCO3 = OFF
        
    ######### GPIO 2 port B Waveform VCO 4 #############
    if tMcp2B & 0xf0 == 0xe0:
        sons.waveFormVCO4 = MODE_SINE
    elif tMcp2B & 0xf0 == 0xd0:
        sons.waveFormVCO4 = MODE_TRIANGLE
    elif tMcp2B & 0xf0 == 0xb0:
        sons.waveFormVCO4 = MODE_CLOCK
    elif tMcp2B & 0xf0 == 0x70:
        sons.waveFormVCO4 = OFF

def check_irq1(i2c):
    global touchedA
    global touchedB
    global touchedC
    global touchedD
    global octaveMPR
    global waveFormLFO1
    
    state = machine.disable_irq()
    #print("State IRQ1: ",hex(state))

    #lire register interruption INTF PORT A
    intfA = i2c.readfrom_mem(_MCP1, _MCP_INTFA, 1)
    #print("Interruption _MCP1_INTFA", hex(bytes_to_int(intfA)))
    intfA = bytes_to_int(intfA)
    
    GPIOA = i2c.readfrom_mem(_MCP1, _MCP_GPIOA, 1)
    GPIOA = bytes_to_int(GPIOA)
    #print("_MCP1_GPIOA: ", hex(GPIOA))
    
    intcapa = i2c.readfrom_mem(_MCP1, _MCP_INTCAPA, 1)
    intcapa = bytes_to_int(intcapa)
    #print("_MCP1_INTCAPA: ", hex(intcapa))
    
    i2c.readfrom_mem(_MCP1, _MCP_GPIOA, 1)
    #printRegister(i2c, _MCP1, _MCP_GPIOA, 1,"_MCP1_GPIOA")
    
    #lire register interruption INTF PORT B
    intfB = i2c.readfrom_mem(_MCP1, _MCP_INTFB, 1)
    #print("Interruption _MCP1_INTFB", hex(bytes_to_int(intfB)))
    intfB = bytes_to_int(intfB)
    #if intfB==0 & intfA==0: return
    
    intcapb = i2c.readfrom_mem(_MCP1, _MCP_INTCAPB, 1)
    #intcapb = bytes_to_int(intcapb)
    ##print("_MCP_INTCAPB: ", hex(intcapb))
    
    GPIOB = i2c.readfrom_mem(_MCP1, _MCP_GPIOB, 1)
    GPIOB = bytes_to_int(GPIOB)
    #print("_MCP1_GPIOB: ", hex(GPIOB))

        
    #IRQ Octave 2eme pot
    if intfA & 0x01 == 0x01:	#_MCP_INTCAPA = 0xfe
        setOctave(0)
    elif intfA & 0x02== 0x02:	#_MCP_INTCAPA = 0xfd
        setOctave(1)
    elif intfA & 0x04 == 0x04:	#_MCP_INTCAPA = 0xfb
        setOctave(2)
    elif intfA & 0x08 == 0x08:	#_MCP_INTCAPA = 0xf7
        setOctave(3)
    
    #Irq modes 1er pot
    if intfB  & 0x01 == 0x01:	#_MCP_INTCAPB = 0xfe
        setMode(sons.tabMode[0]) #monophonique
    elif intfB  & 0x02 == 0x02:	#_MCP_INTCAPB = 0xfd
        setMode(sons.tabMode[1]) #polyphonique
    elif intfB  & 0x04 == 0x04:	#_MCP_INTCAPB = 0xfb
        setMode(sons.tabMode[2]) #sequenceur
    elif intfB  & 0x08 == 0x08:	#_MCP_INTCAPB = 0xf7
        setMode(sons.tabMode[3]) #Portamento
        
    #contacteur LFO 1 GPIOB 3 bits MSB
    #if GPIOB & 0xf0 != 0xf0 and intfB != 0x0:
    if intfB & 0x10 == 0x10:
        waveFormLFO1 = MODE_SINE
        sons.sendLFO(freqLFO1, MODE_SINE)
    if intfB & 0x20 == 0x20:
        waveFormLFO1 = MODE_TRIANGLE
        sons.sendLFO(freqLFO1, MODE_TRIANGLE)
    if intfB & 0x40 == 0x40:
        waveFormLFO1 = MODE_CLOCK
        sons.sendLFO(freqLFO1, MODE_CLOCK)
    if intfB & 0x80 == 0x80:
        waveFormLFO1 = OFF
        sons.sendLFO(0, waveFormLFO1)
    #print("waveFormLFO1: ", waveFormLFO1)
    machine.enable_irq(state)
    

#IRQs contacteurs VCO1 à VCO4 wave form sur MCP2
def check_irq2(i2c):   
    state = machine.disable_irq()
    ##print("State IRQ2: ",hex(state))
    
    #lire register interruption INTF PORT A
    intfA = i2c.readfrom_mem(_MCP2, _MCP_INTFA, 1)
    #print("Interruption _MCP2_INTFA", hex(bytes_to_int(intfA)))
    intfA = bytes_to_int(intfA)
    
    intcapa = i2c.readfrom_mem(_MCP2, _MCP_INTCAPA, 1)
    #intcapa = bytes_to_int(intcapa)
    ##print("_MCP2_INTCAPA: ", hex(intcapa))
    
    GPIOA = i2c.readfrom_mem(_MCP2, _MCP_GPIOA, 1)
    GPIOA = bytes_to_int(GPIOA)
    #print("_MCP2_GPIOA: ", hex(GPIOA))
    
    #lire register interruption INTF PORT B
    intfB = i2c.readfrom_mem(_MCP2, _MCP_INTFB, 1)
    #print("Interruption _MCP2_INTFB", hex(bytes_to_int(intfB)))
    intfB = bytes_to_int(intfB)
    #if intfB==0 & intfA==0: return
    
    intcapb = i2c.readfrom_mem(_MCP2, _MCP_INTCAPB, 1)
    #intcapb = bytes_to_int(intcapb)
    ##print("_MCP2_INTCAPB: ", hex(intcapb))
    
    GPIOB = i2c.readfrom_mem(_MCP2, _MCP_GPIOB, 1)
    GPIOB = bytes_to_int(GPIOB)
    #print("_MCP2_GPIOB: ", hex(GPIOB))
    
    #contacteur VCO 1 GPIOA 4 bits MSB
    if GPIOA & 0xf0 != 0xf0 and intfA != 0x0:
        if intfA & 0x10 == 0x10:	#_MCP_INTCAP 0xef
            sons.waveFormVCO1 = MODE_SINE 
        elif intfA & 0x20 == 0x20:	#_MCP_INTCAP 0xdf
            sons.waveFormVCO1 = MODE_TRIANGLE            
        elif intfA & 0x40 == 0x40:	#_MCP_INTCAP 0x7f
            sons.waveFormVCO1 = MODE_CLOCK            
        elif intfA & 0x80 == 0x80:	#_MCP_INTCAP 0xbf
            sons.waveFormVCO1 = OFF
        print("waveFormVCO1: ", affMode(sons.waveFormVCO1))
        
    #contacteur VCO 2 GPIOA 4 bits LSB
    if GPIOA & 0x0f != 0x0f and intfA != 0x0:
        if intfA & 0x1 == 0x1:	#_MCP_INTCAP 0xef
            sons.waveFormVCO2 = MODE_SINE
        if intfA & 0x2 == 0x2:	#_MCP_INTCAP 0xdf
            sons.waveFormVCO2 = MODE_TRIANGLE
        if intfA & 0x04 == 0x04:	#_MCP_INTCAP 0x7f
            sons.waveFormVCO2 = MODE_CLOCK
        if intfA & 0x08 == 0x08:	#_MCP_INTCAP 0xbf
            sons.waveFormVCO2 = OFF
        print("waveFormVCO2: ", affMode(sons.waveFormVCO2))
        
    #contacteur VCO 3 GPIOB 4 bits LSB
    if GPIOB & 0x0f != 0x0f and intfB != 0x0:
        if intfB & 0x1 == 0x1:	#_MCP_INTCAP 0xef
            sons.waveFormVCO3 = MODE_SINE
        if intfB & 0x2 == 0x2:	#_MCP_INTCAP 0xdf
            sons.waveFormVCO3 = MODE_TRIANGLE
        if intfB & 0x04 == 0x04:	#_MCP_INTCAP 0x7f
            sons.waveFormVCO3 = MODE_CLOCK
        if intfB & 0x08 == 0x08:	#_MCP_INTCAP 0xbf
            sons.waveFormVCO3 = OFF
        print("waveFormVCO3: ", affMode(sons.waveFormVCO3))
        
    #contacteur VCO 4 GPIOB 4bits MSB
    if GPIOB & 0xf0 != 0xf0 and intfB != 0x0:
        if intfB & 0x10 == 0x10:	#_MCP_INTCAP 0xef
            sons.waveFormVCO4 = MODE_SINE
        if intfB & 0x20 == 0x20:	#_MCP_INTCAP 0xdf
            sons.waveFormVCO4 = MODE_TRIANGLE
        if intfB & 0x40 == 0x40:	#_MCP_INTCAP 0x7f
            sons.waveFormVCO4 = MODE_CLOCK
        if intfB & 0x80 == 0x80:	#_MCP_INTCAP 0xbf
            sons.waveFormVCO4 = OFF
        print("waveFormVCO4: ", affMode(sons.waveFormVCO4))
    
    machine.enable_irq(state)