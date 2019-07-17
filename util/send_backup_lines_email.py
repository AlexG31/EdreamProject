#encoding:utf8
import os, sys
import json
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email_util import load_credentials, send_email

def send_json(credential_path, content, subject = 'clean-lines', email_content = ""):
  credentials = load_credentials(credential_path)
  f = credentials['email']
  t = credentials['email']
  p = credentials['pass']
  host = credentials['host']
  port = credentials['port']

  mime_content = MIMEApplication(content, "json")
  html = MIMEText(email_content, "html")
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
  json_path = sys.argv[1]
  credential_path = sys.argv[2]
  print('input json path:', json_path)
  print('input credential path:', credential_path)

  with open(json_path, 'r') as fin:
    data = json.load(fin)
  send_json(credential_path, json.dumps(data), 
    subject=json_path, 
    email_content=parseDreamInfo(data))