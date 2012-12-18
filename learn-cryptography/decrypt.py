import logging
import webapp2
import model
import json
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
        'scramble':getTranslator('kgxmqblwrjnydshzatoeuifpvc')
}
decrypters = {
        'caesar':getRoter(23),
        'railenvy':getRoter(13),
        'oneshot':getRoter(5),
        'mixer':getTranslator('zyxwvutsrqponmlkjihgfedcba'),
        'scramble':getTranslator('qfzmtwbovjagdksxeinruyhclp')
}

def getEncrypter(name):
    return encrypters[name]

def getDecrypter(name):
    return decrypters[name]


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

class DecryptHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("GET was called")

    def post(self):
        text_key = self.request.get('text')
        logging.info('Decrypting text key: %s, with decryption algorithm: %s' % (text_key, self.request.get('decryptor')))
        text = ndb.Key(model.Text, text_key).get()

        if self.request.get('decryptor') == 'rotate':
            decrypted = rotate(text.encrypted, self.request)
        else:
            decrypted = translate(text.encrypted, self.request)
        self.response.out.write(
                json.dumps({'win':check_result(text, decrypted), 'text':decrypted}))

