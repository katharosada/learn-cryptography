#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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


jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

def getTemplateValues():
    template_values = {
        'ciphertext': CIPHER_TEXT.encode('rot13'),
        'cleartext': CIPHER_TEXT
    }
    return  template_values

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(getTemplateValues()))

class LevelHandler(webapp2.RequestHandler):
	  def get(self):
	    	template = jinja_environment.get_template('level.html')
	    	self.response.out.write(template.render(getTemplateValues()))

class AnalysisPaneHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('analysis.html')
        self.response.out.write(template.render(getTemplateValues()))

class TextsPaneHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('texts.html')
        self.response.out.write(template.render(getTemplateValues()))

class DecryptorsPaneHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('decryptors.html')
        self.response.out.write(template.render(getTemplateValues()))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/level', LevelHandler),
    ('/analysis', AnalysisPaneHandler),
    ('/texts', TextsPaneHandler),
    ('/decryptors', DecryptorsPaneHandler),
], debug=True)
