import numpy as np
from time import time

class Speck:
    tailles_blocs = {32: {64: 22},
                      48: {72: 22, 96: 23},
                      64: {96: 26, 128: 27},
                      96: {96: 28, 144: 29},
                      128: {128: 32, 192: 33, 256: 34}}


    def __init__(self, key, tailleClef=128, tailleBloc=128, vecteurInitial=0, counter=0):

        self.tailleBloc = tailleBloc
        self.tailleMot = self.tailleBloc >> 1

        self.rounds = self.tailles_blocs[tailleBloc][tailleClef]
        self.tailleClef = tailleClef

        self.masque = (2 ** self.tailleMot) - 1

        self.masque2 = (2 ** self.tailleMot)

        if self.tailleBloc == 32:
            self.decalageBeta = 2
            self.decalageAlpha = 7
        else:
            self.decalageBeta = 3
            self.decalageAlpha = 8


        self.iv = vecteurInitial & ((2 ** self.tailleBloc) - 1)
        self.iv1 = self.iv >> self.tailleMot
        self.iv2 = self.iv & self.masque

        self.counter = counter & ((2 ** self.tailleBloc) - 1)

        self.key = key & ((2 ** self.tailleClef) - 1)

        self.clefs = [self.key & self.masque]
        preparationClefs = [(self.key >> (x * self.tailleMot)) & self.masque for x in range(1, self.tailleClef // self.tailleMot)]

        for x in range(self.rounds - 1):
            nouvelleClef = self.tourChiffrement(preparationClefs[x], self.clefs[x], x)
            preparationClefs.append(nouvelleClef[0])
            self.clefs.append(nouvelleClef[1])


    def chiffer(self, texteClair):
        b = (texteClair >> self.tailleMot) & self.masque
        a = texteClair & self.masque

        b, a = self.chiffrement(b, a)

        ciphertext = (b << self.tailleMot) + a

        return ciphertext


    def chiffrement(self, x, y):
        for k in self.clefs:
            x,y = self.tourChiffrement(x, y, k)
        return x,y

    def tourChiffrement(self, x, y, k):
        rs_x = ((x << (self.tailleMot - self.decalageAlpha)) + (x >> self.decalageAlpha)) & self.masque
        add_sxy = (rs_x + y) & self.masque
        x2 = k ^ add_sxy
        ls_y = ((y >> (self.tailleMot - self.decalageBeta)) + (y << self.decalageBeta)) & self.masque
        y2 = x2 ^ ls_y

        return x2, y2

    def dechiffer(self, ciphertext):

        b = (ciphertext >> self.tailleMot) & self.masque
        a = ciphertext & self.masque

        b, a = self.dechiffrement(b, a)

        texteClair = (b << self.tailleMot) + a

        return texteClair

    def dechiffrement(self, x, y):
        for k in reversed(self.clefs):
            x,y = self.tourDechiffrement(x, y, k)

        return x,y

    def tourDechiffrement(self, x, y, k):
        y2 = (((x ^ y) << (self.tailleMot - self.decalageBeta)) + ((x ^ y) >> self.decalageBeta)) & self.masque
        msub = (((x ^ k) - y2) + self.masque2) % self.masque2
        x2 = ((msub >> (self.tailleMot - self.decalageAlpha)) + (msub << self.decalageAlpha)) & self.masque

        return x2, y2

    def update_iv(self, new_iv):
        self.iv = new_iv & ((2 ** self.tailleBloc) - 1)
        self.iv1 = self.iv >> self.tailleMot
        self.iv2 = self.iv & self.masque


def testPerformance():
    nBlocs = 1000000000
    algo = Speck(0x1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100, 256, 128)
    t1 = time()

    for x in np.random.randint(0,2**16,(1,nBlocs)):
        algo.chiffer(int(x[0]))

    dt = time() - t1
    volumeChiffre = nBlocs / 1e6
    debit = volumeChiffre / dt

    print("\nTest de performance : {} Mio/s".format(debit))

if __name__ == "__main__":
    algo = Speck(0x1f1e1d1c1b1a191817161514131211100f0e0d0c0b0a09080706050403020100, 256, 128)

    clair = 0x65736f6874206e49202e72656e6f6f70
    chiffree = algo.chiffer(clair)
    dechiffree = algo.dechiffer(chiffree)

    print("Message initial :   " + hex(clair))
    print("Message chiffre :   " + hex(chiffree))
    print("Message dechiffre : " + hex(dechiffree))


    testPerformance()
