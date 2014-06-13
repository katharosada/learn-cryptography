import logging
import webapp2
import model
from google.appengine.ext import ndb

import string


def getRoter(n):
    lc = string.lowercase
    uc = string.uppercase
    trans = string.maketrans(lc + uc, lc[n:] + lc[:n] + uc[n:] + uc[:n])
    return lambda s: string.translate(s, trans)

def getTranslator(aleph):
    lc = string.lowercase
    uc = string.uppercase
    trans = string.maketrans(lc + uc, aleph + aleph.upper())
    return lambda s: string.translate(s, trans)


encrypters = {
        'caesar':getRoter(3),
        'railenvy':getRoter(13),
        'oneshot':getRoter(21),
        'mixer':getTranslator('zyxwvutsrqponmlkjihgfedcba'),
        'scramble':getTranslator('kgxmqblwrjnydshzatoeuifpvc'),
        'upinasi':getTranslator('ecdfighjoklmnpuqrstvawxyzb')
}
decrypters = {
        'caesar':getRoter(23),
        'railenvy':getRoter(13),
        'oneshot':getRoter(5),
        'mixer':getTranslator('zyxwvutsrqponmlkjihgfedcba'),
        'scramble':getTranslator('qfzmtwbovjagdksxeinruyhclp'),
        'upinasi':getTranslator('uzbcadfgehjklminpqrsotvwxy')
}

def getEncrypter(name):
    return encrypters[name]

def getDecrypter(name):
    return decrypters[name]

def decrypt(text, decryptor):
    """Runs a decryptor, depending on the selected decryptor in the data.
    Expects a text and a dictionary like this:
    decryptor: {'id': '<id>', 'key':{<decryptor specific key info>}}
    """
    text = text.encode('ascii', 'ignore').strip()
    if decryptor['id'] == 'rotate':
        return getRoter(int(decryptor['key']['rotate']))(text)
    elif decryptor['id'] == 'translate':
        aleph = "".join([decryptor['key'][a] or '-' for a in string.lowercase])
        return getTranslator(aleph)(text)
    else:
      return "Sorry, that's not a valid decryptor"

def rotate(text, request):
    rot = int(request.get('rotate'))
    text = text.encode('ascii', 'ignore').strip()
    return getRoter(rot)(text)

def translate(text, request):
    aleph = "".join([request.get(a) or '-' for a in string.lowercase])
    logging.info(aleph)
    text = text.encode('ascii', 'ignore').strip()
    return getTranslator(aleph)(text)


def check_result(text, decrypted_text):
    if decrypted_text.strip() == text.content.strip():
        return True
    return False

