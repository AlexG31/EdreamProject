#encoding:utf8
import os, sys
import json
import argparse
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email_util import load_credentials, send_email

def send_json(credential_path, content, 
  subject = 'clean-lines', 
  email_content = ""):
  credentials = load_credentials(credential_path)
  f = credentials['email']
  destination_list = credentials['dest']
  if len(destination_list) == 0:
    destination_list.append(f)
  p = credentials['pass']
  host = credentials['host']
  port = credentials['port']

  mime_content = MIMEApplication(content, "json")
  html = MIMEText(email_content, "html")
  for t in destination_list:
    print('Sending mail to {}'.format(t))
    send_email(f, t, subject, p, host, port, mime_content, [html,])

def parseDreamInfo(dream):
  text = '<h1>=== Dream Info ===</h1>\n'
  text += '<p>total <b>{}</b> lines</p>\n'.format(len(dream))
  text += '<p>last 30 lines:</p>'
  for l in dream[-30:]:
    text += '<br>\n<p>{}</p>\n'.format(l[0])
    text += '<p>[{}]</p>\n'.format(l[1])
  
  return text

if __name__ == '__main__':
  psr = argparse.ArgumentParser()
  psr.add_argument('-json_path', nargs = 1, help = 'json file to send')
  psr.add_argument('-credential_path', nargs = 1, help = 'email credential file')
  input_args = vars(psr.parse_args())

  json_path = input_args['json_path'][0]
  credential_path = input_args['credential_path'][0]
  print('input json path:', json_path)
  print('input credential path:', credential_path)

  with open(json_path, 'r') as fin:
    data = json.load(fin)
  send_json(credential_path, json.dumps(data), 
    subject=json_path, 
    email_content=parseDreamInfo(data)
    )