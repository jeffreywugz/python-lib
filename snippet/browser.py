#!/usr/bin/python

import sys
import time
import exceptions, traceback
import re
import subprocess
import threading
import urllib, urllib2
import cookielib
import HTMLParser
# fix the bug caused by "cjk encode"
HTMLParser.attrfind = re.compile(
      r'\s*([a-zA-Z_][-.:a-zA-Z_0-9]*)(\s*=\s*'
      r'(\'[^\']*\'|"[^"]*"|[-a-zA-Z0-9./,:;+*%?!&$\(\)_#=~@\xA1-\xFE]*))?')
from urlparse import urljoin

class FormExtractor(HTMLParser.HTMLParser):
    def __init__(self, match_request):
        self.match_request, self.in_form, self.vars = match_request, False, {}
        HTMLParser.HTMLParser.__init__(self)

    def form_match(self, attrs):
        return set(self.match_request.items()) <= set(attrs)
        
    def handle_starttag(self, tag, attrs):
        if tag == 'form' and self.form_match(attrs):
            attrs = dict(attrs)
            self.action  = attrs["action"]
            self.in_form = True
        if not self.in_form: return
        if not (tag == 'input' and ('type', 'hidden') in attrs): return
        attrs = dict(attrs)
        self.vars[attrs['name']] = attrs['value']

    def handle_endtag(self, tag):
        if not self.in_form: return
        if tag == 'form': self.in_form = False

class Browser(object):
    default_user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.8) Gecko/20100202 Firefox/3.5.8 GTB6 (.NET CLR 3.5.30729)"
    def __init__(self, user_agent=default_user_agent, http_proxy="", https_proxy=""):
        self.headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5'
        }
        self.http_proxy, self.https_proxy = http_proxy, https_proxy
        self.opener = self.make_opener(self.http_proxy, self.https_proxy)

    @staticmethod
    def make_url(base, **kw):
        return base + '?' + urllib.urlencode(kw)
        
    @staticmethod
    def make_opener(http_proxy, https_proxy):
        proxy_handler = urllib2.ProxyHandler({'http': http_proxy, 'https': https_proxy})
        # proxy_auth_handler = urllib2.ProxyBasicAuthHandler()
        # proxy_auth_handler.add_password('realm', 'host', 'username', 'password')
        cj=cookielib.CookieJar()
        return urllib2.build_opener(proxy_handler, urllib2.HTTPCookieProcessor(cj))

    @staticmethod
    def save_as(html, file_name):
        f = open(file_name, 'w')
        f.write(html)
        f.close()

    @staticmethod
    def display(file_name):
        subprocess.call("firefox %s"%(file_name), shell=True)
        
    @staticmethod
    def display_as(html, file_name):
        Browser.save_as(html, file_name)
        Browser.display(file_name)
        
    def get_page(self, url, data=None):
        if data: data = urllib.urlencode(data)
        request = urllib2.Request(url, data, self.headers)
        return self.opener.open(request).read()

    def form_submit(self, url, submit_vars, form_match_request={}):
        source_page = self.get_page(url)
        form_extractor = FormExtractor(form_match_request)
        form_extractor.feed(source_page)
        action = urljoin(url, form_extractor.action)
        form_extractor.vars.update(submit_vars)
        submit_vars = form_extractor.vars
        response = self.get_page(action, submit_vars)
        return self.maybe_jump(response)

    def maybe_jump(self, html):
        url_repr = re.search('location\.replace\("(.+)"\)', html)
        if not url_repr: return html
        url = eval("\'%s\'"%url_repr.group(1))
        return self.get_page(url)

def gae_auth(browser, url, email, passwd):
    f = browser.form_submit(url,  dict(Email="huafengxi@gmail.com", Passwd="314975802"),
                            dict(id="gaia_loginform"))
    
if __name__ == '__main__':
    url = "http://fate-stay-night.appspot.com/shell"
    http_proxy = 'http://10.10.44.251:6588'
    https_proxy = 'http://10.10.44.251:6588'
    browser = Browser(http_proxy=http_proxy, https_proxy=https_proxy)
    gae_auth(browser, url, "huafengxi@gmail.com", "314975802")
    result = browser.get_page(url, dict(expr="2+2"))
    browser.display_as(result, "result.html")
