#encoding:utf8
import os, sys
import json
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email_util import load_credentials, send_email

def send_json(credential_path, content, subject = 'clean-lines', mime_type = "html"):
  credentials = load_credentials(credential_path)
  f = credentials['email']
  t = credentials['email']
  p = credentials['pass']
  host = credentials['host']
  port = credentials['port']

  mime_content = MIMEApplication(content, "json")
  send_email(f, t, subject, p, host, port, mime_content)


if __name__ == '__main__':
  json_path = sys.argv[1]
  credential_path = sys.argv[2]
  print('input json path:', json_path)
  print('input credential path:', credential_path)

  with open(json_path, 'r') as fin:
    data = json.load(fin)
  send_json(credential_path, json.dumps(data), subject=json_path)