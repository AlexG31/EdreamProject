#encoding:utf8
import os, sys
import json
import argparse
import pdb
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
  psr.add_argument('-in', type=str, help = 'in')
  psr.add_argument('-out', type=str, help = 'out')
  input_args = vars(psr.parse_args())

  in_path = input_args['in']
  out_path = input_args['out']

  with open(in_path, 'r') as fin:
    data = json.load(fin)

  with open(out_path, 'w', encoding='utf8') as fout:
    lines = [x[0] for x in data]
    json.dump(lines, fout, indent = 4, ensure_ascii=False)
  print('done.')