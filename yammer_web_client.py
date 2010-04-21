#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import simplejson
from yammer import Yammer, YammerError
import local_settings
import logging
logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger('yammer_web_client')

__author__ = 'Jai Vikram Singh Verma'
__license__ = "MIT"
__version__ = '0.1'
__email__ = "jaivikram.verma@gmail.com"


class YammerWebClient(object):
    def __init__(self, access_token_key = None, access_token_secret = None):
        self.consumer_key = local_settings.CONSUMER_KEY
        self.consumer_secret = local_settings.CONSUMER_SECRET
        self.access_token_key = access_token_key
        self.access_token_secret = access_token_secret
        try:
            self.yammer = Yammer(self.consumer_key, 
                                 self.consumer_secret,
                                 access_token_key = access_token_key, 
                                 access_token_secret = access_token_secret)
        except YammerError, m:
            log.debug("*** Error: %s" % m.message)
        
    def fetchRequestToken(self):
        try:
            unauth_request_token = self.yammer.fetch_request_token()
        except YammerError, m:
            log.debug("*** Error: %s" % m.message)

        unauth_request_token_key = unauth_request_token.key
        unauth_request_token_secret = unauth_request_token.secret
        
        try:
            auth_url = self.yammer.get_authorization_url(unauth_request_token)
        except YammerError, m:
            log.debug("*** Error: %s" % m.message)
        return {'unauth_request_token_key': unauth_request_token_key,
                'unauth_request_token_secret': unauth_request_token_secret,
                'auth_url': auth_url}

    def fetchAccessToken(self, unauth_request_token_key,
                         unauth_request_token_secret,
                         oauth_verifier):
        try:
            access_token = self.yammer.\
                fetch_access_token(unauth_request_token_key,
                                   unauth_request_token_secret,
                                   oauth_verifier)
        except YammerError, m:
            log.debug("*** Error: %s" % m.message)
            
        access_token_key = access_token.key
        access_token_secret = access_token.secret
        #use these to reconstruct the Yammer object and get the user details
        return {'access_token_key': access_token_key,
                'access_token_secret': access_token_secret}

    def __verifyInitialCreds(self):
        if self.access_token_key and self.access_token_secret:
            return True

    def fetchUserPosts(self):
        if not self.__verifyInitialCreds():
            raise YammerError(\
                message = "no access token and/or key provided")
        try:
            posts = self.yammer.get_user_posts(max_length=1),
            #username=username,
            #include_replies=include_replies)
            log.info(simplejson.dumps(posts, indent=4))
            return posts
        except YammerError, m:
            log.debug("*** Error: %s" % m.message)



