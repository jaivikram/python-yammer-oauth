"""
Pre-requisites
For testing this you must have Tornado installed
http://github.com/facebook/tornado
"""

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado import httpclient
from yammer_web_client import YammerWebClient, simplejson

from tornado.options import define, options

__author__ = 'Jai Vikram Singh Verma'
__license__ = "MIT"
__version__ = '0.1'
__email__ = "jaivikram.verma@gmail.com"

define("port", default=8888, help="run on the given port", type=int)


class YAuth(tornado.web.RequestHandler):
    def get(self):
        ywc = YammerWebClient()
        return self.render("testwebclient.html", **ywc.fetchRequestToken())

    def getAccessTokenAsync(self, callback):
        ywc = YammerWebClient()
        res = ywc.fetchAccessToken(self.get_argument('unauth_request_token_key'),
                                   self.get_argument('unauth_request_token_secret'),
                                   self.get_argument('oauth_verifier'))
        return callback(res)
        #Wanted to do some more async http here
        #but the yammer.Yammer.fetch_access_token is made sync
        # will need to write a modified version of that to provide only the
        # url and not make the sync requests.
        #http = httpclient.AsyncHTTPClient()
        #http.fetch(url, self.async_callback(
        #        self._on_authentication_verified, callback))

    def _on_authentication_verified(self, callback):
        pass

    def post(self):
        self.getAccessTokenAsync(self.async_callback(self._on_auth))
        return
    
    def _on_auth(self, res):
        ywc = YammerWebClient(access_token_key = res['access_token_key'],
                              access_token_secret = res['access_token_secret']) 
        posts = ywc.fetchUserPosts()
        self.set_header("Content-Type", "application/json")
        return self.write(simplejson.dumps(posts))


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/yauth/", YAuth),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
