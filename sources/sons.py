from ad9833 import *
from machine import Pin

notes = ([
  [32.70, 34.65, 36.71, 38.89, 41.20, 43.65, 46.25, 49.00, 51.91, 55.00, 58.27, 61.74], #octave 0
  [65.41, 69.30, 73.42, 77.78, 82.41, 87.31, 92.50, 98.00,103.83, 110.00, 116.54, 123.47], #octave 1
  [130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.00, 233.08, 246.94], #octave 2
  [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392.00, 415.30, 440.00, 466.16, 493.88], #octave 3
  [523.25, 554.37, 587.33, 622.25, 659.26, 698.46, 739.99, 783.99, 830.61, 880.00, 932.33, 987.77], #octave 4
  [1046.5,1108.7,1174.7,1244.5,1318.5,1396.9,1480,1568,1661.2,1760,1864.7,1975.5], #octave 5
  [2093.0,2217.5,2349.3,2489,2637,2793.8,2960,3136,3322.4,3520,3729.3,3951.1] #octave 7
]);

ad_cs = [12, 27, 14, 15, 32]
tab_ssel = []
tab_gen = []

tabTouche = [0,0,0,0] # mémoire des touches jouées pour les 4 VCOs
#octaveMPR = 0

octave_offset=0

oldToucheA = 0
oldToucheB = 0
oldToucheC = 0
oldToucheD = 0

tabMode = ['MONO','POLY','SEQU','PORTA','HARMO']
mode = tabMode[0]

etatGate = 0 #etat de la gate
pinGate = 4 #no de pin physique sur esp32

waveFormVCO1 = MODE_SINE
waveFormVCO2 = MODE_SINE
waveFormVCO3 = MODE_SINE
waveFormVCO4 = MODE_SINE

VCO5 = const(4) # position du CS dans TAB oscillateurs pour LFO

def resetTabNotes():
    for i in range(len(tabTouche)):
        tabTouche[i]=0
        
def testVCOs(MODE, freqVCO, freqLFO):            #tests VCOs
    sendSignal(tab_gen[0], 0, MODE, freqVCO, 0) #VCO1
    sendSignal(tab_gen[1], 0, MODE, freqVCO, 0)
    sendSignal(tab_gen[2], 0, MODE, freqVCO, 0)
    sendSignal(tab_gen[3], 0, MODE, freqVCO, 0)
    sendSignal(tab_gen[VCO5], 0, MODE_TRIANGLE, freqLFO, 0) # LFO

def initAd9833(spi):
    for i in range(0, 5):
        ssel = Pin(ad_cs[i], Pin.OUT, value=1)
        tab_ssel.append(ssel)
        tab_gen.append(AD9833( spi, tab_ssel[i])) # default clock at 25 MhZ
        sendSignal(tab_gen[i], 0, MODE_SINE, 0, 0)
    return tab_gen

def sendGate(pin_Gate):
    global etatGate    
    
    if etatGate == 0:
        etatGate = 1
        #pin_Gate.value(1)
        pin_Gate = Pin(pinGate, mode=Pin.OUT, value=1)
    else:
        etatGate = 0
        #pin_Gate.value(0)
        pin_Gate = Pin(pinGate, mode=Pin.OUT, value=0)
    #print(etatGate, pin_Gate.value())

def sendLFO(freq, waveFormLFO1):
    global tab_gen
    
    sendSignal(tab_gen[VCO5], 0, waveFormLFO1, freq, 0)
    return

def sendSignal(gen, reg, mode, freq, phase):
    # Suspend Output
    gen.reset = True

    # Configure Freq0
    gen.select_register(reg)
    gen.mode = mode
    gen.freq = freq
    gen.phase = phase

    # Activate output on Freq0
    gen.select_register(reg)
    gen.reset = False
    
def sendVCOs(tnote, status):
    global tab_gen
    global ocatveMPR
    global mode
    double = False
    
    if mode == "MONO":
        if status == "RELEASED":
            #tnote = 0
            pin_Gate = Pin(pinGate, mode=Pin.OUT, value=0)
        else:
            pin_Gate = Pin(pinGate, mode=Pin.OUT, value=1)
            sendSignal(tab_gen[0], 0, waveFormVCO1, tnote, 0) #VCO1
            sendSignal(tab_gen[1], 0, waveFormVCO2, tnote * 2, 0) #VCO2 harmonique rang 1
            sendSignal(tab_gen[2], 0, waveFormVCO3, tnote * 3, 0) #VCO3 harmonique rang 2
            sendSignal(tab_gen[3], 0, waveFormVCO4, tnote * 4, 0) #VCO4 harmonique rang 3
            
        
    elif mode =="POLY":
        if len(tabTouche) < 5 and status=="PRESSED":
            for j in range(len(tabTouche)):
                if tabTouche[j] == tnote:
                    double = True
                    return
            if not double:
                for j in range(len(tabTouche)):   
                    if tabTouche[j]==0:
                        tabTouche[j] = tnote
                        break
                    
            pin_Gate = Pin(pinGate, mode=Pin.OUT, value=1)
            
            sendSignal(tab_gen[0], 0, waveFormVCO1, tabTouche[0], 0) #VCO1
            sendSignal(tab_gen[1], 0, waveFormVCO2, tabTouche[1], 0) #VCO2 harmonique rang 1
            sendSignal(tab_gen[2], 0, waveFormVCO3, tabTouche[2], 0) #VCO3 harmonique rang 2
            sendSignal(tab_gen[3], 0, waveFormVCO4, tabTouche[3], 0) #VCO4 harmonique rang 3
            
        elif status == "RELEASED":
            for j in range(len(tabTouche)):
                if tnote == tabTouche[j] :
                    tabTouche[j]=0
            
            pin_Gate = Pin(pinGate, mode=Pin.OUT, value=0)
                
        #print("STATUS:", status, tnote)        
        #for k in range(len(tabTouche)):
            #print("tabTouche:", tabTouche[k])
            
    else:
        print("MODE NON SUPPORTE")

def check(touche, oldTouche, octaveMPR, dac1):
    global octave_offset
    global tabTouche
    global mode
    
    
    #print("Touched:", hex(touche), "oldTouche: ",oldTouche)
    diff = oldTouche ^ touche
    for i in range(12):
        if diff & (1 << i):
            if touche & (1<<i):
                #print('Key {} pressed'.format(i))
                nb_octaves = octave_offset + octaveMPR
                CV_Step = 256 / 84
                CV_tension = (0.4714285714285714 * nb_octaves) + (0.0392857142857143 * i)
                index = (nb_octaves * 12) + i
                CV = index * CV_Step
                dac1.write(int(CV))
                #print(index, CV_Step, CV, CV_tension, ":", nb_octaves, octave_offset, octaveMPR, i)
                
                tnote = notes[nb_octaves][i]
                sendVCOs(tnote,"PRESSED")
                if mode == "MONO":
                    break
            else:
                #print('Key {} released'.format(i))
                tnote = notes[octave_offset + octaveMPR][i]
                sendVCOs(tnote,"RELEASED")
    return touche
    
def pollingKBD(mpr121_A, mpr121_B, mpr121_C, mpr121_D, dac1):
    global oldToucheA
    global oldToucheB
    global oldToucheC
    global oldToucheD
    
    toucheA = mpr121_A.touched()
    if toucheA != oldToucheA:
        octaveMPR = 0
        #print("Touched:", toucheA, "oldTouche: ",oldToucheA)
        oldToucheA = check(toucheA, oldToucheA, octaveMPR, dac1)
        #print("Touched:", toucheA, "oldTouche: ",oldToucheA)
        
    toucheB = mpr121_B.touched()
    if toucheB != oldToucheB:
        octaveMPR = 2
        oldToucheB = check(toucheB, oldToucheB, octaveMPR, dac1)
        
    toucheC = mpr121_C.touched()
    if toucheC != oldToucheC:
        octaveMPR = 1
        oldToucheC = check(toucheC, oldToucheC, octaveMPR, dac1)
        
    toucheD = mpr121_D.touched()
    if toucheD != oldToucheD:
        octaveMPR = 3
        oldToucheD = check(toucheD, oldToucheD, octaveMPR, dac1)