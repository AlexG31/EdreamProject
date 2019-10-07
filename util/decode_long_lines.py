#encoding:utf8
import os, sys
import json
import argparse
import pdb
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email_util import load_credentials, send_email

if __name__ == '__main__':
  psr = argparse.ArgumentParser()
  psr.add_argument('-in', type=str, help = 'in')
  psr.add_argument('-out', type=str, help = 'out')
  psr.add_argument('-threshold', type=int, default=100, help = 'out')
  input_args = vars(psr.parse_args())

  in_path = input_args['in']
  out_path = input_args['out']
  threshold = input_args['threshold']

  with open(in_path, 'r') as fin:
    data = json.load(fin)

  cnt = 0
  with open(out_path, 'w', encoding='utf8') as fout:
    lines = [x[0] for x in data]
    for l in lines:
      if len(l) >= threshold:
        cnt += 1
        fout.write(l + '\n')

  print('total {} long lines'.format(cnt))
  print('done.')