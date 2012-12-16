import webapp2
import os
import jinja2

CIPHER_TEXT = """
It is unknown how effective the Caesar cipher was at the time, but it is likely to have been reasonably secure, not least because most of Caesar's enemies would have been illiterate and others would have assumed that the messages were written in an unknown foreign language.[4] There is no record at that time of any techniques for the solution of simple substitution ciphers. The earliest surviving records date to the 9th century works of Al-Kindi in the Arab world with the discovery of frequency analysis.[5]
A Caesar cipher with a shift of one is used on the back of the Mezuzah to encrypt the names of God. This may be a holdover from an earlier time when Jewish people were not allowed to have Mezuzahs. The letters of the cryptogram themselves comprise a religiously significant "divine name" which Orthodox belief holds keeps the forces of evil in check.[6]
In the 19th century, the personal advertisements section in newspapers would sometimes be used to exchange messages encrypted using simple cipher schemes. Kahn (1967) describes instances of lovers engaging in secret communications enciphered using the Caesar cipher in The Times.[7] Even as late as 1915, the Caesar cipher was in use: the Russian army employed it as a replacement for more complicated ciphers which had proved to be too difficult for their troops to master; German and Austrian cryptanalysts had little difficulty in decrypting their messages.[8]
Caesar ciphers can be found today in children's toys such as secret decoder rings. A Caesar shift of thirteen is also performed in the ROT13 algorithm, a simple method of obfuscating text widely found on Usenet and used to obscure text (such as joke punchlines and story spoilers), but not seriously used as a method of encryption.[9]
The Vigenere cipher uses a Caesar cipher with a different shift at each position in the text; the value of the shift is defined using a repeating keyword. If the keyword is as long as the message, chosen random, never becomes known to anyone else, and is never reused, this is the one-time pad cipher, proven unbreakable. The conditions are so difficult they are, in practical effect, never achieved. Keywords shorter than the message (e.g., "Complete Victory" used by the Confederacy during the American Civil War), introduce a cyclic pattern that might be detected with a statistically advanced version of frequency analysis.[10]
In April 2006, fugitive Mafia boss Bernardo Provenzano was captured in Sicily partly because some of his messages, written in a variation of the Caesar cipher, were broken. Provenzano's cipher used numbers, so that "A" would be written as "4", "B" as "5", and so on.[11]
In 2011, Rajib Karim was convicted in the United Kingdom of "terrorism offences" after using the Caesar cipher to communicate with Bangladeshi Islamic activists discussing plots to blow up British Airways planes or disrupt their IT networks. Although the parties had access to far better encryption techniques (Karim himself used PGP for data storage on computer disks), they chose to use their own scheme instead (implemented in Microsoft Excel) "because 'kaffirs', or non-believers, know about it [ie, PGP] so it must be less secure".
"""

import model
import decrypt

from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


results = {}

default_levels = []

level_list = None

defaultLevels = ['caesar']

def getOrCreateLevel(level_key):
    level = level_key.get()
    if not level:
        level = model.Level(key=level_key)
    return level

def resetTexts():
    key = ndb.Key(model.Text, 'caesar')
    text = key.get()
    if not text:
        text = model.Text(key=key)
    text.name = "Caesar Cipher Wikipedia Text"
    ct = CIPHER_TEXT.encode('ascii','ignore')
    text.content = ct
    text.encrypted = decrypt.getEncrypter('caesar')(ct)
    text.put()

    key = ndb.Key(model.Text, 'railenvy')
    text = key.get();
    if not text:
        text = model.Text(key=key)
    text.name = "Rail Envy"
    text.content = open('texts/texts/railenvy.txt', 'rU').read()
    text.encrypted = decrypt.getEncrypter('railenvy')(text.content)
    text.put()

def resetAllTheThings():
    global default_levels
    global level_list

    resetTexts()

    level_list_key = ndb.Key(model.LevelSequence, model.LEVEL_LIST)
    level_list = level_list_key.get()
    if not level_list:
        # Create level list with level 1
        level_list = model.LevelSequence(key=level_list_key)
        level_list.name = 'default'
        level_list.put()

    # Level 1
    l1key = ndb.Key(model.Level, 'caesar')
    if not l1key in level_list.levels:
        level_list.levels.append(l1key)
        level_list.put()

    level1 = getOrCreateLevel(l1key)
    level1.name = "Julius Caesar"
    level1.startstory = open('texts/start/caesar.txt', 'rU').read()
    level1.endstory = open('texts/end/caesar.txt', 'rU').read()
    level1.text = ndb.Key(model.Text, 'caesar')
    key = level1.put()
    results['level1'] = level1

    # Level 2
    l2key = ndb.Key(model.Level, 'railenvy')
    if not l2key in level_list.levels:
        level_list.levels.append(l2key)
        level_list.put()

    level2 = getOrCreateLevel(l2key)
    level2.name = "Rail Envy"
    level2.startstory = open('texts/start/railenvy.txt', 'rU').read()
    level2.endstory = open('texts/end/railenvy.txt', 'rU').read()
    level2.text = ndb.Key(model.Text, 'railenvy')
    level2.put()
    results['level2'] = level2



class ResetHandler(webapp2.RequestHandler):
    def get(self):
        resetAllTheThings()

        values = {'results':results, 'levels':default_levels, 'level_list':level_list}

        template = jinja_environment.get_template('reset.html')
        self.response.out.write(template.render(values))

app = webapp2.WSGIApplication([
    ('/resetdata', ResetHandler),
], debug=True)
