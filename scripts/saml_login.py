#!/usr/bin/env python3
import requests
from urllib.parse import urlparse, parse_qs
from sys import stdin
import json

from helpers.timer import Timer
from helpers.HTMLForm import HTMLForm


# Debug
#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.DEBUG)

def is_SAMLRequest(response):
    args = urlparse(response.url).query
    return ('SAMLRequest' in (parse_qs(args).keys()))

def report_and_exit(message,status,channels=[]):
    result = {
            "version": 2,
            "status": status,
            "message": message,
    }
    if status == "ok":
        id = 0
        result["channels"] = []
        for ch in channels:
            id += 10
            ch["id"] = id
            ch["type"] = "integer"
            ch["kind"] = "time_milliseconds"
            result["channels"].append(ch)

    print(json.dumps(result))
    exit()

if __name__ == "__main__":
    # The parameters are sp login url, sp logout url, application host, # username, password
    params = stdin.readline().rstrip().split(',')
    login, logout, apphost, username, password = params

    timer = Timer()
    channels = []

    # A Get request to the login url of the app should redirect the user to the
    # IFP. The latter will respond with a login form.
    step = 'Redirect to IDP'
    r_app = requests.get(f'https://{apphost}/{login}')
    find_saml_redir = (r for r in r_app.history + [r_app] if is_SAMLRequest(r))
    saml_redirect = next(find_saml_redir, None)
    if saml_redirect is None:
        report_and_exit(step,'error')

    idp = urlparse(saml_redirect.url).netloc
    message = f'idp: {idp}'
    loginform = HTMLForm(r_app,'loginform')
    if loginform.form is None:
        report_and_exit('Loginform not found', 'error')
    channels.append({'name': step, 'value': timer.get_elapsed()})

    # We submit the filled in login form to the IDP
    step = 'IdP login'
    form_data = { 'username': username, 'password': password }
    r_login = loginform.submit(form_data)
    # The IDP login response always has status code 200, even when the login failed
    # Succesfull login is indicated by the presence of the cookie
    # 'SimpleSAMLAuthToken'
    auth_token = r_login.cookies.get('SimpleSAMLAuthToken', None)
    if not auth_token:
        report_and_exit(step ,'error')
    channels.append({'name':step, 'value': timer.get_elapsed()})
    # The IDP response contains a form that needs to be submitted to the
    # service provider. (In the browser this is automated by a javascript script)
    saml_form = HTMLForm(r_login)
    saml_form.add_cookies(loginform.cookiejar)

    step = 'Application login'
    r_app = saml_form.submit()
    # succesfull saml post to the service provider assertion consumer url
    # results in a redirect to a succesful app session (r_app.ok = True).
    # The response should not redirect back to the idp (this is common behaviour
    # when the post of the SamlLoginResponse fails and would not be detected if
    # in check on r_app.ok) unless the sp is also idp.
    find_idp_redir = (r for r in r_app.history
        if urlparse(r.headers['location']).netloc == idp)
    redirected_to_idp = apphost != idp and next(find_idp_redir, None)
    if redirected_to_idp or not r_app.ok:
        report_and_exit(step, 'error')
    channels.append({'name': step, 'value': timer.get_elapsed()})

    # A Get request on the logout url will redirect to the IDP for
    # terminating the session there
    step = 'IdP Logout'
    r_logout = requests.get('https://{}/{}'.format(apphost,logout),
            cookies=saml_form.cookiejar)
    find_saml_redir = (r for r in r_logout.history if is_SAMLRequest(r) and
        urlparse(r.url).netloc == idp)
    saml_redirect = next(find_saml_redir, None)
    if saml_redirect is None:
        report_and_exit(step, 'error')
    channels.append({'name': step, 'value': timer.get_elapsed()})

    # After logout on the IDP, the IDP will redirect to the logout consumer of
    # the application.
    step = 'Application logout'
    saml_logout_form = HTMLForm(r_logout)
    saml_logout_form.add_cookies(saml_form.cookiejar)
    r_app = saml_logout_form.submit()
    find_response_error = (r for r in r_app.history + [r_app] if not r.ok)
    response_error = next(find_response_error, None)
    if response_error != None:
        report_and_exit(step, 'error')
    channels.append({'name': step, 'value': timer.get_elapsed()})
    report_and_exit(message, 'ok', channels)

