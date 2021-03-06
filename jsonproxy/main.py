#!/usr/bin/env python
# Copyright 2009 Google Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re
import wsgiref.handlers
import xml.dom.minidom
import simplejson
import xml2json

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template


# Matches an acceptable JSONp callback
_CALLBACK_REGEX = re.compile(r'[\w\.\[\]]+')


def FetchUrlContent(url):
  """Returns the string fetched from the given URL.

  Uses the urlfetch interface to get the contents of a given URL.  The
  memcache version will be returned if recent.

  Args:
    url: The url to fetch.

  Raises:
    LookupError: The URL was not able to be fetched.
  """
  content = memcache.get(url)
  if content:
    return content

  request = urlfetch.fetch(url)

  if request.status_code == 200:
    content = request.content
    memcache.add(url, content, 60 * 60)
    return content

  raise LookupError('Unable to fetch URL. Response code: ' +
                    str(request.status_code))


def FetchJsonFromUrl(url):
  """Returns a JSON string representing an XML document at the given URL.

  Args:
    url: The url of an XML document to fetch.

  Raises:
    LookupError: The URL was not able to be fetched.
    SyntaxError: The XML document had bad syntax.
  """
  doc_str = FetchUrlContent(url)
  doc = xml.dom.minidom.parseString(doc_str)
  doc_json = xml2json.DocumentToJson(doc)

  return doc_json


class HomeHandler(webapp.RequestHandler):
  """Handles the root index page."""

  def get(self):
    """Writes out the root page"""
    self.response.out.write(
      self.response.out.write(template.render('index.tpl', {})))


class ProxyHandler(webapp.RequestHandler):
  """Handles the proxy form (/proxy)."""

  def get(self):
    """Handle a proxy request."""
    callback = None

    try:
      url = self.request.get('url')
      tmp_callback = self.request.get('callback')
      if (tmp_callback is not None and 
          _CALLBACK_REGEX.match(tmp_callback)):
        callback = tmp_callback
      json = FetchJsonFromUrl(url)

    # We don't want to just 500 on an error, we still need to return valid
    # JSON or our users will get JavaScript errors.
    except Exception, e:
      self.response.set_status(503)
      json = simplejson.dumps({'$error': str(e)})

    # Wrap as JSONp if requested
    if callback is not None:
      json = '%s(%s)' % (callback, json)

    self.response.headers.add_header(
      'Content-Type', 'application/javascript')
    self.response.out.write(json)


class TemplateHandler(webapp.RequestHandler):
  """Handler that just serves a template."""

  def __init__(self, template_path):
    """Create a handler that serves the provided template.

    Args:
      template_path: The path to the template.
    """
    self.template_path = template_path

  def get(self):
    """Serves the template"""
    self.response.out.write(template.render(self.template_path, {}))


class AboutHandler(TemplateHandler):
  """Serves the about page."""

  def __init__(self):
    TemplateHandler.__init__(self, 'about.tpl')


class ExamplesHandler(TemplateHandler):
  """Serves the examples page."""

  def __init__(self):
    TemplateHandler.__init__(self, 'examples.tpl')


class AmazonExampleHandler(TemplateHandler):
  """Serves the Amazon example page."""
  
  def __init__(self):
    TemplateHandler.__init__(self, 'amazon.tpl')


def main():
  application = webapp.WSGIApplication([
      ('/', HomeHandler),
      ('/about', AboutHandler),
      ('/proxy', ProxyHandler),
      ('/examples', ExamplesHandler),
      ('/examples/amazon', AmazonExampleHandler)
      ], debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
