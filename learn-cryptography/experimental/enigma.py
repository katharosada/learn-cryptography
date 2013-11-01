
import string


# Enigma I rotors:
ROTOR_I_WIRING = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
ROTOR_I_NOTCH = "Q"
ROTOR_II_WIRING = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
ROTOR_II_NOTCH = "E"
ROTOR_III_WIRING = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
ROTOR_III_NOTCH = "V"
ROTOR_IV_WIRING = "ESOVPZJAYQUIRHXLNFTGKDCMWB"
ROTOR_IV_NOTCH = "J"
ROTOR_V_WIRING = "VZBRGITYUPSDNHLXAWMJQOFECK"
ROTOR_V_NOTCH = "Z"

# M4 extra wheels (used for navy)
ROTOR_VI_WIRING = "JPGVOUMFYQBENHZRDKASXLICTW"
ROTOR_VI_NOTCH = "ZM"
ROTOR_VII_WIRING = "NZJHGRCXMYSWBOUFAIVLPEKQDT"
ROTOR_VII_NOTCH = "ZM"
ROTOR_VIII_WIRING = "FKQHTLXOCBJSPDZRAMEWNIUYGV"
ROTOR_VIII_NOTCH = "ZM"
ROTOR_BETA_WIRING = "LEYJVCNIXWPBQMDRTAKZGFUHOS"
ROTOR_BETA_NOTCH = "" # Beta wheel doesn't rotate
ROTOR_GAMMA_WIRING = "FSOKANUERHMBTIYCWLQPZXVGJD"
ROTOR_GAMMA_NOTCH = "" # doesn't rotate

# M4 Reflectors
REFLECTOR_UKW_B_WIRING = "ENKQAUYWJICOPBLMDXZVFTHRGS"
REFLECTOR_UKW_C_WIRING = "RDOBJNTKVEHMLFCWZAXGYIPSUQ"


# Comercial Enigma rotors:
ROTOR_IC = "DMTWSILRUYQNKFEJCAZBPGXOHV"
ROTOR_IIC = "HQZGPJTMOBLNCIFDYAWVEUSRKX"
ROTOR_IIIC = "UQNTLSZFMREHDPXKIBVYGJCWOA"

REFLECTOR_A_WIRING = "EJMZALYXVBWFCRQUONTSPIKHGD"
REFLECTOR_B_WIRING = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
REFLECTOR_C_WIRING = "FVPJIAOYEDRZXWGCTKUQSBNMHL"

ALPH = string.uppercase

class DiskSlots(object):
    def __init__(self, disk_list, reflector, steckers):
        self.disk_list = disk_list
        self.reflector = reflector
        self.steckers = {}
        for pair in steckers:
            pair = pair.upper()
            self.steckers[pair[0]] = pair[1]
            self.steckers[pair[1]] = pair[0]
###            print "Adding stecker pair: (%s, %s)" % (pair[0], pair[1])

    def setRotorPositions(self, positions):
        assert len(positions) == len(self.disk_list)
        positions = positions.upper()
        for ch, disk in zip(positions, self.disk_list):
            disk.setRotation(ch)

    def setRingStellung(self, stellung):
        assert len(stellung) == len(self.disk_list)
        stellung = stellung.upper()
        for ch, disk in zip(stellung, self.disk_list):
            disk.setRingStellung(ch)
        

    def stecker(self, ch):
        ch = ch.upper()
        if ch in self.steckers:
            return self.steckers[ch]
        return ch

    def type(self, ch):
    
        ch = self.stecker(ch)

        # Rotate the rotors
        # Note that due to double-stepping, the middle rotor (position 1) will
        # always turn whenever the leftmost (position 0) turns.
        rotate_1 = False
        rotate_0 = False
        if self.disk_list[2].isNotchOpen():
            rotate_1 = True
        if self.disk_list[1].isNotchOpen():
            rotate_0 = True
            rotate_1 = True

        self.disk_list[2].rotate()
        if rotate_1:
            self.disk_list[1].rotate()
        if rotate_0:
            self.disk_list[0].rotate()

        # Encrypt the letter
        ch = ch.upper()
        for d in self.disk_list[::-1]:
            ch = d.crypt(ch)

        ch = self.reflector.crypt(ch)

        for d in self.disk_list:
            ch = d.reverseCrypt(ch)
        return self.stecker(ch)

    def printWindows(self):
        windows = [disk.window() for disk in self.disk_list]
        return "Windows: " + str(windows)
           


class Disk(object):
    def __init__(self, rotor_wiring, notch=""):
        self.wiring = rotor_wiring
        self.mapping = {}
        self.reverse_mapping = {}
        self.notch = notch
        self.rotation = 0
        self.setRingStellung('A')

    def setRingStellung(self, ringPos):
        ringPos = ALPH.index(ringPos.upper())
        self.ringStellung = ringPos
        for i, ch in enumerate(ALPH):
            self.mapping[ch] = self.wiring[i]
            self.reverse_mapping[self.wiring[i]] = ch

    def setRotation(self, ch):
###        self.rotation = (ALPH.index(ch) - self.ringStellung + 26) % 26
        self.rotation = ALPH.index(ch)

    def window(self):
        return ALPH[self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % 26

    def isNotchOpen(self):
        if ALPH[self.rotation] in self.notch:
            return True
        return False
    
    def _getRotated(self, ch):
        ch = ch.upper()
        index = (ALPH.index(ch) + self.rotation - self.ringStellung + 26) % 26
        letter = ALPH[index]
        return letter

    def _getUnRotated(self, ch):
        ch = ch.upper()
        index = (ALPH.index(ch) - self.rotation + self.ringStellung + 26) % 26
        letter = ALPH[index]
        return letter

    def crypt(self, ch):
        # get rotated letter
        letter = self._getRotated(ch)
        res = self.mapping[letter]
        # Unrotate the response
        return self._getUnRotated(res)

    def reverseCrypt(self, ch):
        letter = self._getRotated(ch)
        res = self.reverse_mapping[letter]
        return self._getUnRotated(res)

def test():
    disk = Disk(ROTOR_I_WIRING, ROTOR_I_NOTCH)
    res = disk.crypt("e")
    print res

ROTOR_I = Disk(ROTOR_I_WIRING, ROTOR_I_NOTCH)
ROTOR_II = Disk(ROTOR_II_WIRING, ROTOR_II_NOTCH)
ROTOR_III = Disk(ROTOR_III_WIRING, ROTOR_III_NOTCH)
ROTOR_IV = Disk(ROTOR_IV_WIRING, ROTOR_IV_NOTCH)
ROTOR_V = Disk(ROTOR_V_WIRING, ROTOR_V_NOTCH)
REFLECTOR_A = Disk(REFLECTOR_A_WIRING)
REFLECTOR_B = Disk(REFLECTOR_B_WIRING)
REFLECTOR_C = Disk(REFLECTOR_C_WIRING)

ROTOR_VI = Disk(ROTOR_VI_WIRING, ROTOR_VI_NOTCH)
ROTOR_VII = Disk(ROTOR_VII_WIRING, ROTOR_VII_NOTCH)
ROTOR_VIII = Disk(ROTOR_VIII_WIRING, ROTOR_VIII_NOTCH)
ROTOR_BETA = Disk(ROTOR_BETA_WIRING) # No notch
ROTOR_GAMMA = Disk(ROTOR_GAMMA_WIRING) # No notch
REFLECTOR_UKW_B = Disk(REFLECTOR_UKW_B_WIRING)
REFLECTOR_UKW_C = Disk(REFLECTOR_UKW_C_WIRING)



if __name__ == "__main__":

    DEFAULT_STECKS = "BL CK DG FP IR MO QW ST VY UZ"
    stecks = raw_input("Stecker board configuration (e.g. AJ BU): ")
    if stecks == "":
        stecks = DEFAULT_STECKS
    stecks = stecks.split()
###    TEST_SETUP = DiskSlots([ROTOR_I, ROTOR_II, ROTOR_III], REFLECTOR_B, stecks)
###    TEST_SETUP = DiskSlots([ROTOR_IV, ROTOR_III, ROTOR_II], REFLECTOR_B, stecks)
###    TEST_SETUP = DiskSlots([ROTOR_III, ROTOR_II, ROTOR_I], REFLECTOR_B, stecks)
    # M4 example setup:
###    TEST_SETUP = DiskSlots([ROTOR_VIII, ROTOR_II, ROTOR_IV], REFLECTOR_B, stecks)

    TEST_SETUP = DiskSlots([ROTOR_III, ROTOR_V, ROTOR_I], REFLECTOR_B, stecks)

    # A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
    # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
    # A = 1, Z = 26
    # 19   7   12
    #  S   G    L

    # (Spruchschlussel)
    # WTG - PLT
    # JIS,YCY


    ringStellung = raw_input("Ringstellung? ")
    TEST_SETUP.setRingStellung(ringStellung.strip())

    inp = raw_input("Rotor initial state (e.g. ABC): ")
    TEST_SETUP.setRotorPositions(inp.strip())

    inp = raw_input(">>> ")
    while inp:
        letters = []
        for ch in inp.strip():
            if ch.isalpha():
              letters.append(TEST_SETUP.type(ch))
###        print "".join(letters).replace('X', ' ')
        print "".join(letters)
        inp = raw_input(">>> ")


