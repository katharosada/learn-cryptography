
import string
import copy


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

class Enigma(object):
    """A generic implementation of a WWII Enigma machine."""
    def __init__(self, rotor_list, reflector, steckers=None):
        self.rotor_list = [copy.deepcopy(r) for r in rotor_list]
        self.reflector = copy.deepcopy(reflector)
        self.steckers = {}
        if steckers is not None:
            self.setSteckers(steckers)

    def setSteckers(self, steckers):
        """Set the pairs of stecker plugs.
        Takes a list of pairs of letters, representing which letter should be
        swapped (plugged together) with which other letter."
        """
        for pair in steckers:
            pair = pair.upper()
            self.steckers[pair[0]] = pair[1]
            self.steckers[pair[1]] = pair[0]

    def setRotorPositions(self, positions):
        """Set the positions of the rotors.
        The length of the positions string must match the number of rotors in
        this Enigma. The postions should be given as a string  where
        each characters is the letter that is visible at the top of the rotor
        in the desired position."""
        assert len(positions) == len(self.rotor_list)
        positions = positions.upper()
        for ch, disk in zip(positions, self.rotor_list):
            disk.setRotation(ch)

    def setRingStellung(self, stellung):
        """Set the Ringstellung for each rotor.
        The Ringstellung only controls the rotation between the visible
        letters and the mechanism of the rotor, which includes the internal
        wiring and the notch which triggers the rotation of the rotor. This
        function expects a string of the characters representing the rotation,
        if you see the Ringstellung as numbers, 1=A, 2=B and so on."""
        assert len(stellung) == len(self.rotor_list)
        stellung = stellung.upper()
        for ch, disk in zip(stellung, self.rotor_list):
            disk.setRingStellung(ch)
        
    def _stecker(self, ch):
        ch = ch.upper()
        if ch in self.steckers:
            return self.steckers[ch]
        return ch

    def _typeChar(self, ch):
    
        ch = self._stecker(ch)

        # Rotate the rotors
        # Note that due to double-stepping, the middle rotor (position 1) will
        # always turn whenever the leftmost (position 0) turns.
        rotate_1 = False
        rotate_0 = False
        if self.rotor_list[-1].isNotchOpen():
            rotate_1 = True
        if self.rotor_list[-2].isNotchOpen():
            rotate_0 = True
            rotate_1 = True

        self.rotor_list[-1].rotate()
        if rotate_1:
            self.rotor_list[-2].rotate()
        if rotate_0:
            self.rotor_list[-3].rotate()

        # Encrypt the letter
        ch = ch.upper()
        for d in self.rotor_list[::-1]:
            ch = d.crypt(ch)

        ch = self.reflector.crypt(ch)

        for d in self.rotor_list:
            ch = d.reverseCrypt(ch)
        return self._stecker(ch)

    def type(self, inp):
        letters = []
        for ch in inp.strip():
            if ch.isalpha():
              letters.append(self._typeChar(ch))
        return "".join(letters)

    def printWindows(self):
        """Returns a string, showing the current face up ring positions for
        each rotor."""
        windows = [disk.window() for disk in self.rotor_list]
        return "Windows: " + str(windows)


class Rotor(object):
    """A single rotor for an Enigma machine. 
    Stores its own state for its current ringstellung and rotation."""

    def __init__(self, rotor_wiring, notch=""):
        self.wiring = rotor_wiring
        self.mapping = {}
        self.reverse_mapping = {}
        self.notch = notch
        self.rotation = 0
        self.setRingStellung('A')

    def setRingStellung(self, ringPos):
        """Set the Ringstellung for this rotor."""
        ringPos = ALPH.index(ringPos.upper())
        self.ringStellung = ringPos
        for i, ch in enumerate(ALPH):
            self.mapping[ch] = self.wiring[i]
            self.reverse_mapping[self.wiring[i]] = ch

    def setRotation(self, ch):
        """Set the number of steps that this has been rotated from the 'A'
        position."""
###        self.rotation = (ALPH.index(ch) - self.ringStellung + 26) % 26
        self.rotation = ALPH.index(ch)

    def window(self):
        """The current letter facing up on the rotor.
        This is effectively the Alpha representation of the rotation of the
        Rotor from 'A'."""
        return ALPH[self.rotation]

    def rotate(self):
        """Rotate the rotor 1 step."""
        self.rotation = (self.rotation + 1) % 26

    def isNotchOpen(self):
        """True if the rotation of this rotor is such that the notch is open
        causing the next rotor to rotate. Note that some rotors have multiple
        notches or none."""
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
        """Resolve the transformation of the current coming right-to-left
        through this rotor."""
        # get rotated letter
        letter = self._getRotated(ch)
        res = self.mapping[letter]
        # Unrotate the response
        return self._getUnRotated(res)

    def reverseCrypt(self, ch):
        """Resolve the transformation of the current coming left-to-right
        through this rotor."""
        letter = self._getRotated(ch)
        res = self.reverse_mapping[letter]
        return self._getUnRotated(res)


ROTOR_I = Rotor(ROTOR_I_WIRING, ROTOR_I_NOTCH)
ROTOR_II = Rotor(ROTOR_II_WIRING, ROTOR_II_NOTCH)
ROTOR_III = Rotor(ROTOR_III_WIRING, ROTOR_III_NOTCH)
ROTOR_IV = Rotor(ROTOR_IV_WIRING, ROTOR_IV_NOTCH)
ROTOR_V = Rotor(ROTOR_V_WIRING, ROTOR_V_NOTCH)
REFLECTOR_A = Rotor(REFLECTOR_A_WIRING)
REFLECTOR_B = Rotor(REFLECTOR_B_WIRING)
REFLECTOR_C = Rotor(REFLECTOR_C_WIRING)

ROTOR_VI = Rotor(ROTOR_VI_WIRING, ROTOR_VI_NOTCH)
ROTOR_VII = Rotor(ROTOR_VII_WIRING, ROTOR_VII_NOTCH)
ROTOR_VIII = Rotor(ROTOR_VIII_WIRING, ROTOR_VIII_NOTCH)
ROTOR_BETA = Rotor(ROTOR_BETA_WIRING) # No notch
ROTOR_GAMMA = Rotor(ROTOR_GAMMA_WIRING) # No notch
REFLECTOR_UKW_B = Rotor(REFLECTOR_UKW_B_WIRING)
REFLECTOR_UKW_C = Rotor(REFLECTOR_UKW_C_WIRING)



if __name__ == "__main__":

    DEFAULT_STECKS = "BL CK DG FP IR MO QW ST VY UZ"
    stecks = raw_input("Stecker board configuration (e.g. AJ BU): ")
    if stecks == "":
        stecks = DEFAULT_STECKS
    stecks = stecks.split()
###    TEST_SETUP = Enigma([ROTOR_I, ROTOR_II, ROTOR_III], REFLECTOR_B, stecks)
###    TEST_SETUP = Enigma([ROTOR_IV, ROTOR_III, ROTOR_II], REFLECTOR_B, stecks)
###    TEST_SETUP = Enigma([ROTOR_III, ROTOR_II, ROTOR_I], REFLECTOR_B, stecks)
    # M4 example setup:
###    TEST_SETUP = Enigma([ROTOR_VIII, ROTOR_II, ROTOR_IV], REFLECTOR_B, stecks)

    TEST_SETUP = Enigma([ROTOR_II, ROTOR_I, ROTOR_III], REFLECTOR_A, stecks)


    # A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
    # 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6
    # A = 1, Z = 26
    # 19   7   12
    #  S   G    L
    # XMV

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


