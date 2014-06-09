import webapp2
import os


class PrintEnvironmentHandler(webapp2.RequestHandler):
    """Dumps out the environment variables for debug purposes."""
    def get(self):
       for name in os.environ.keys():
          self.response.out.write("%s = %s<br />\n" % (name, os.environ[name]))


app = webapp2.WSGIApplication([
  ('/debug/env', PrintEnvironmentHandler),
], debug=True)
