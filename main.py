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
import jinja2
import os
import re

from google.appengine.ext import db
# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

class Posted(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        t = jinja_env.get_template('mainBlog.html')
        content = t.render()
        self.response.write(content)

class MainBlog(webapp2.RequestHandler):
    def get(self):
        posts = db.GqlQuery('SELECT * FROM Posted ORDER BY created DESC LIMIT 5')
        t = jinja_env.get_template('mainBlog.html')
        content = t.render(posts = posts)
        if self.request.path == '/blog':
            self.redirect('/blog/')
            return
        self.response.write(content)

class NewPost(webapp2.RequestHandler):
    def get(self):
        t = jinja_env.get_template('newBlog.html')
        content = t.render()
        self.response.write(content)
    def post(self):
        title = self.request.get('subject')
        post = self.request.get('content')
        if title and post:
            p = Posted(title = title,content = post)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = 'Make sure you fill subject AND the post'
            t = jinja_env.get_template('newBlog.html')
            content = t.render(subject = title, content = post, error = error)
            self.response.write(content)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Posted.get_by_id(int(id))
        t = jinja_env.get_template('permalink.html')
        content = t.render(post = post)
        if not post:
            t = jinja_env.get_template('error.html')
            content = t.render(post = id)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog/?', MainBlog),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
    ('/blog/newpost', NewPost)
], debug=True)
