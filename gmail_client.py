'''
Hackingly stolen from the Gmail API examples. -zrc
'''

from __future__ import print_function
import httplib2
import os
import time
import datetime
import sys
import traceback
import json
from sendEmail import CreateMessage,SendMessage
from apiclient import discovery

import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

FROM = 'Bob the Job Scobbler <bobthejobscobbler@gmail.com>'
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Bob the Job Scobbler'

#def get_credentials():
"""Gets valid user credentials from storage.

If nothing has been stored, or if the stored credentials are invalid,
the OAuth2 flow is completed to obtain the new credentials.

Returns:
    Credentials, the obtained credential.
"""
def get_service():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'gmail-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=SCOPES)
        flow.user_agent = APPLICATION_NAME        
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail','v1',http=http)
    return service

def send_message(to, content):
    service = get_service()
    message = CreateMessage('Bob the Job Scobbler', to, datetime.date.today().strftime('Jobs report for %A, %B %d, %Y'), content)
    SendMessage(service, 'bob.the.job.scobbler@gmail.com', message)
    print('Sent mail at ' + time.ctime() + ' to ' + to)

def send_current_user(user=None):
    if user is None:
        user = os.getcwd().split('/')[-1]
    try:
        with open(user + '.email') as f:
            content = f.read()
        with open(user + '.json') as f:
            j = json.loads(f.read())
            to = j['email'][0]
        send_message(to, content)
    except:
        print('Could not send email for %s' % user)
        #traceback.print_last()
        return
    try:
        with open(user + '.to.be.sent') as f:
            with open(user + '.sent','w') as f_out:
                f_out.write(f.read())
    except:
        print('Could not write sent email to .sent file for ' + user)

def send_all(test=False):
    #iterate through all user folders
    os.chdir('users')
    users = os.listdir()
    for user in users:
        if test and user not in ['example']:
            continue
        elif not test and user in ['example']:
            continue
        os.chdir(user)
        send_current_user(user)
        os.chdir('..')
    os.chdir('..')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_all(sys.argv[1] == "test")
    else:
        send_all()




