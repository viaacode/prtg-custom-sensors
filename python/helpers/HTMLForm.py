# Parses a [response object](https://2.python-requests.org/en/master/) in order
# to programmatically fill in and submit forms. The supplied form
# data will be combined with hidden form data during submit.
# It was designed to automate a SAML login.
#
# Usage:
#
# import requests
# from HTMLForm import HTMLForm

# url='https://app.example.net
# r = requests.get(url)
#
# # submit the SAML login form
# loginform = HTMLForm(r,'loginform')
# data = { 'username': 'beautifuluser',
#          'password': 'strongpassword' }
# r = f.submit(data)

# # Submit the SAML response to the service provider app.
# samlresponseform = HTMLForm(r)
# r = samlresponseform.submit()

# Requirements:
# - Python 3.4
# - requests
# - pyquery
# It is compatible with Python 3.4 as this version of python is used
# by the monitoring system @VIAA.
import requests
from urllib.parse import urlparse, urljoin
from pyquery import PyQuery as pq

class HTMLForm(object):

    def __init__(self,response,formid=None):
        self.response = response
        self.cookiejar = requests.cookies.RequestsCookieJar()
        self.add_response_cookies(response)
        # Use the html parser, because the default parser does not handle xhtml
        doc = pq(response.text, parser='html')
        selector = 'form#{}'.format(formid) if formid else 'form'
        form = doc(selector)
        self.form = form[0] if form else None

    # Add cookies from a requests.cookies.RequestsCookieJar to our cookiejar
    def add_cookies(self,cookies):
        self.cookiejar.update(cookies)

    # Add all cookies, also those that were set during redirections, from an
    # arbitrary response object to our cookiejar.
    def add_response_cookies(self,response):
        for resp in response.history + [response]:
            self.add_cookies(resp.cookies)

    # the base url of the document, without parameters or query
    def get_base_url(self):
        c = urlparse(self.response.url)
        return '{}://{}{}'.format(c.scheme,c.netloc,c.path)

    # Resolve the form action url, which can be relative or absolute
    def get_action_url(self):
        url = self.form.action
        return urljoin(self.get_base_url(), url)

    # Submit the form, including 'hidden' input field values and the cookies
    # For example the SAML Login Response is POSTED to the SP as a form with
    # hidden fields.
    def submit(self,data=[]):
        # Fill in the form with the provided data
        data_tuples = data if (type(data) is list) else list(data.items())
        for id, value in data_tuples:
          try:
            el = self.form.get_element_by_id(id)
          except KeyError:
            # Temporary fallback needed because the login form in the simplesaml1.x
            # theme does not contain input field id's.
            el = next(x for x in self.form.iter() if x.get('name') == id)
          el.value = value
        # Submit the filled in Form
        resp = requests.post(self.get_action_url(),
                data = self.form.form_values(),
                cookies = self.cookiejar,
                headers = { 'referer': self.response.url})
        self.add_response_cookies(resp)
        return resp
