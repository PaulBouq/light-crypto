#coding: UTF-8

### SPONGENT 160/160/80 ###

import time #used to measure time of hash

class Spongent():
    def __init__(self, n = 160, b = 240, r = 80, lfsr = 0x01):
        #default values of SPONGENT 160 / 160 /80
        self.sbox = ['e', 'd', 'b', '0', '2', '1', '4', 'f', '7', 'a', '8', '5', '9', 'c', '3', '6'] #S-Box of SPONGENT
        self.b = b
        self.B = b/8
        self.n = n
        self.r = r
        self.state = 0
        self.lfsr = lfsr
        self.blocs = []

    def initialisation(self,message):
        #initialize the algorithm with 1 and 0 padding
        for i in range(len(message)):
            self.state = self.state + (ord(message[i])<<8*i)
        #padding du state
        if(len(bin(self.state))-2 != self.r):
            self.state = (self.state << 1) + 1
            self.state = self.state << (self.r - ((len(bin(self.state))-2) % self.r))
        #LFSR initialization below
        self.lfsr = 0x01 #CAS DU SPONGENT 160 / 160 / 80

    def nextLFSR(self):
        #return next value of lfsr, based on primitive polynom 1 + x + x² + x³ + x⁷
        return ((self.lfsr << 1)|(((self.lfsr >> 1)^(self.lfsr >> 2)^(self.lfsr >> 3)^(self.lfsr >> 7))&1)) % 256

    def reverse(self, nb):
        #reverse the 8-bit number in entry of function (used for the lfsr)
        nb = ((nb & 0xf0)>>4) |((nb&0x0f)<<4)
        nb = ((nb & 0xcc)>>2) |((nb&0x33)<<2)
        return ((nb & 0xaa)>>1)|((nb&0x55)<<1)

    def pLayer(self):
        #pLayer step of the algorithm
        chainebinaire = bin(self.state)[2:]
        if(len(chainebinaire)<self.b):
            chainebinaire += '0'*(self.b-len(chainebinaire))
        chaineret = ""
        for i in range(len(chainebinaire)):
            if(chainebinaire[i]!='L'):
                if((i%self.b) <= (self.b - 2)):
                    chaineret = chaineret + chainebinaire[(i * self.b / 4) % (self.b - 1)]
                else:
                    chaineret = chaineret + chainebinaire[self.b-1]
                    
        #update of self.state    
        self.state = int(chaineret,2)

    def passageSBox(self):
        #sBox step
        chainehexa = hex(self.state)[2:]
        chaineret = ""
        for i in range(len(chainehexa)):
            if(chainehexa[i]!='L'):
                chaineret= chaineret + (self.sbox[int(chainehexa[i],16)])
        self.state = int(chaineret,16)

    def stepone(self):
        #step 1 of the round, iCounter xor state xor retnuoCi
        chainebinaire = bin(self.state)[2:]
        revLFSR = self.reverse(self.lfsr) << (len(chainebinaire) - 8)
        self.state = self.state ^ self.lfsr
        self.state = self.state ^ revLFSR
        #next value for LFSR
        self.lfsr = self.nextLFSR()
        if(self.lfsr == 0xff):
            #reset du LFSR
            self.lfsr = 0x01

    def hach(self,msg):
        self.initialisation(msg)
        chainebinaire = bin(self.state)[2:]
        for i in range(0,len(chainebinaire),self.r):
            self.blocs.append(int(chainebinaire[i:i+self.r],2))
        #Splitting message in r-bits blocs
        for j in range(len(self.blocs)):
            self.state = self.state ^ self.blocs[j]
            #permutation PI(b) of R rounds 
            for k in range(self.r):
                self.stepone()
                self.passageSBox()
                self.pLayer()
        #absorption is done, let's move to "squeezing" phase
        squeeze = 0
        cpt = 0
        while(len(bin(squeeze)[2:]) < self.n):
            chainetmp = bin(self.state)
            chainetmpbis = chainetmp[2:self.r+2]
            squeeze = squeeze + (int(chainetmpbis,2) << (cpt * self.r))
            for k in range(self.r):
                self.stepone()
                self.passageSBox()
                self.pLayer()
            cpt = cpt + 1
        return squeeze

if(__name__=="__main__"):
    message = "Hello, world !"
    spg = Spongent()
    t1 = time.time()
    hach = spg.hach(message)
    t2 = time.time()

    print("Valeur du hach :")
    print(hex(hach)[2:len(hex(hach))-1])
    print("temps de calcul :")
    print(t2-t1)


        
