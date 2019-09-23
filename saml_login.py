# -*- coding: utf-8 -*-
import requests
from urllib.parse import urlparse, parse_qs
from helpers.HTMLForm import HTMLForm
from helpers.timer import Timer
import sys
import json
# get CustomSensorResult from paepy package
from paepy.ChannelDefinition import CustomSensorResult

def is_SAMLRequest(response):
    args = urlparse(response.url).query
    return ('SAMLRequest' in (parse_qs(args).keys()))

def report_and_exit(message,channels):
    result = CustomSensorResult(message)
    # The final step reports elapsed time of the full login/logout sequence
    # Make it the primary channel
    # The value is set to 0 when an error was encounterd. Setting the
    # limit_min_error = 1 will trigger the error state for the channel in PRTG.
    channels.reverse()
    for ch in channels:
        result.add_channel(channel_name=ch['name'], unit='ms',
                value=ch['value'], is_float=False, is_limit_mode=True,
                limit_min_error=1, limit_max_error=5000,
                limit_min_warning=0, limit_max_warning=3000,
                limit_error_msg=ch.get('error', 'Timeout'))

    print(result.get_json_result())
    exit()

if __name__ == "__main__":
    # interpret first command line parameter as json object
    data = json.loads(sys.argv[1])
    login, logout = data['params'].split(',')
    timer = Timer()
    channels = []

    step = 'Redirect to IDP'
    r_app = requests.get('https://{}/{}'.format(data['host'],login))
    saml_redirect = (next(( r for r in r_app.history + [r_app]
        if is_SAMLRequest(r)), None))
    if not saml_redirect:
        message = 'Not redirected to idp'
        channels.append({ 'name': step, 'value': 0,
            'error': '{}: {}'.format(r_app.url, r_app.status_code)
            })
        report_and_exit(message,channels)

    message = 'idp: {}'.format(urlparse(saml_redirect.url).netloc)
    loginform = HTMLForm(r_app,'loginform')
    if loginform.form is None:
        channels.append({'name': step, 'value': 0,
            'error': 'loginform not found in idp response' })
        report_and_exit(message,channels)
    channels.append({'name': step, 'value': timer.get_elapsed()})

    step = 'IDP login'
    form_data = {
            'username': data['linuxloginusername'],
            'password': data['linuxloginpassword']
            }
    r_login = loginform.submit(form_data)
    # This response always has status code 200, even when the login failed
    # Succesfull login is iindicated by the presence of the cookie
    # 'SimpleSAMLAuthToken'
    auth_token = r_login.cookies.get('SimpleSAMLAuthToken', None)
    if not auth_token:
        channels.append({'name': step, 'value': 0,
            'error': 'IDP Login failed, check credentieals'
            })
        report_and_exit(message,channels)
    channels.append({'name':step, 'value': timer.get_elapsed()})
    saml_form = HTMLForm(r_login)
    saml_form.add_cookies(loginform.cookiejar)

    step = 'Application login'
    r_app = saml_form.submit()
    # SAML login response always returns HTTP status 200
    # But succesfull saml login results in  a redirect to the app
    redirected = (next(( r for r in r_app.history
        if urlparse(r.headers['location']).netloc == data['host']), None))
    if not redirected:
        channels.append({'name': step, 'value': 0,
            'error': 'IDP does not redirect to application'
            })
        report_and_exit(message,channels)
    channels.append({'name': step, 'value': timer.get_elapsed()})

    step = 'IDP Logout'
    r_logout = requests.get('https://{}/{}'.format(data['host'],logout),
            cookies=saml_form.cookiejar)
    saml_redirect = (next(( r for r in r_logout.history if is_SAMLRequest(r)), None))
    if saml_redirect == None:
        channels.append({'name': step, 'value': 0,
            'error': 'Application does not send logout request to IDP'
            })
        report_and_exit(message,channels)
    channels.append({'name': step, 'value': timer.get_elapsed()})

    step = 'Application logout'
    saml_logout_form = HTMLForm(r_logout)
    saml_logout_form.add_cookies(saml_form.cookiejar)
    r_app = saml_logout_form.submit()
    response_errors = (next(( r for r in r_app.history + [r_app] if not r), None))
    if response_errors != None:
        channels.append({'name': step, 'value': 0,
            'error': 'Final application logout fails'
            })
        report_and_exit(message,channels)
    channels.append({'name': step, 'value': timer.get_elapsed()})
    report_and_exit(message,channels)
