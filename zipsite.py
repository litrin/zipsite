#!/bin/env python
#
# Copyright (c) 2011, Zipsite Project Group All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     # Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     # Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     # Neither the name of the Zipsite Project nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE GROUP AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE GROUP AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##
##    This is a project for Google App Engine 
##        that support create a webisite by ZIP packages!
##
##    By Litrin J. 2011/02
##    Website: http://code.google.com/p/zipsite
##

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext import db
from zipfile import ZipFile
from lib.DataStore import DBCache
from lib import LoadConfig
from lib.MemCache import CacheURL
from lib.LoadFile import NoCached
import os
import logging


class MainHandler(webapp.RequestHandler):

    URLString = ''
    IndexPage = LoadConfig.getStr('zipsite', 'DefaultPage')
    NoErrors = True

    def get(self):
    
        self.URLString=self.request.path
        
        if ( self.URLString[-1:] == '/'):
        #Get the defaule file for the path
            self.URLString += self.IndexPage       
            
        DBHandle = DBCache()
        (sMimeType, Entry) = DBHandle.load(self.URLString) 
        
        if (Entry is not None):
            logging.info("Load: " + self.URLString + " From Cached!")
                        
        else:
            try:
                (sMimeType, Entry) = NoCached().load(self.URLString)
                
            except NameError:
                self.pageNoFound()
                self.NoErrors = False
           
        if (self.NoErrors):
            self.response.headers['Content-Type'] = str(sMimeType)
            self.response.out.write(Entry)
            #Response building finished!
        
    def pageNoFound(self):
        logging.info('404 Page no found at ' + self.URLString)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write('<h1>404 Page No Found!</h1>')


def main():
    application = webapp.WSGIApplication([
                            ('.*', MainHandler),
                                ], 
                                                    debug=True)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
