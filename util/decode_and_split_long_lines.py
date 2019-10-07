#encoding:utf8
import os, sys
import json
import argparse
import pdb
import re

lengthThreshold = 100
quotes = set([
  '"',
  u'“',
  u'”',
  u'‘',
  u'�'
])
startMarks = re.compile(r'^[ ]*[\.\:\;\,]+')

def removeMarks(line):
  line = startMarks.sub('', line)
  result = ''
  for ch in line:
    if ch in quotes:
      continue
    result += ch
  return result

def splitComma(line):
  result = []
  n = len(line)
  phrase = ''
  for ind, ch in enumerate(line):
    phrase += ch
    if ch == ',':
      if ind + 1 < n and line[ind + 1] == ' ':
        result.append(phrase)
        phrase = ''

  if len(phrase) > 0:
    result.append(phrase)

  # SplitByAnd
  shorten = []
  for l in result:
    l = l.strip(' \r\n')
    if len(l) >= lengthThreshold:
      splitAnd = lambda x: splitWord(x, target = 'and')
      splitBut = lambda x: splitWord(x, target = 'but')
      splitBecause = lambda x: splitWord(x, target = 'because')
      splitOr = lambda x: splitWord(x, target = 'or')
      sub = procImpl(l, splitAnd)
      sub = procImpl(sub, splitBut)
      sub = procImpl(sub, splitBecause)
      sub = procImpl(sub, splitOr)
      shorten.extend(sub)
    else:
      shorten.append(l)

  return result

def split(line):
  line = removeMarks(line)
  result = []
  n = len(line)
  phrase = ''
  for ind, ch in enumerate(line):
    phrase += ch
    if ch == '.':
      if ind + 1 < n and line[ind + 1] == ' ':
        if ind + 2 >= n or line[ind + 2].isupper():
          result.append(phrase)
          phrase = ''

  if len(phrase) > 0:
    result.append(phrase)

  # SplitByComma
  shorten = []
  for l in result:
    l = l.strip(' \r\n')
    if len(l) >= lengthThreshold:
      shorten.extend(splitComma(l))
    else:
      shorten.append(l)
      
  if all([len(l) < lengthThreshold for l in shorten]):
    return shorten
  else:
    return None

def splitWord(line, target = 'and'):
  result = []

  phrases = []
  words = line.split(' ')
  for w in words:
    if w.lower() == target:
      result.append(' '.join(phrases))
      phrases = []
    phrases.append(w)

  if len(phrases) > 0:
    result.append(' '.join(phrases))

  return result

def getLongLines(data):
  cnt = 0
  lines = [x[0] for x in data]
  longs = []
  for l in lines:
    if len(l) >= threshold:
      cnt += 1
      longs.append(l)
  print('total {} long lines'.format(cnt))
  return longs

def procImpl(lines, func):
  result = []
  for l in lines:
    sub = func(l)
    if sub:
      result.extend(sub)

  return result

def proc(lines):
  result = procImpl(lines, split)

  return result
    
if __name__ == '__main__':
  psr = argparse.ArgumentParser()
  psr.add_argument('-in', type=str, help = 'in')
  psr.add_argument('-out', type=str, help = 'out')
  input_args = vars(psr.parse_args())

  in_path = input_args['in']
  out_path = input_args['out']
  threshold = lengthThreshold

  with open(in_path, 'r') as fin:
    data = json.load(fin)

  longs = getLongLines(data)
  with open(out_path, 'w', encoding='utf8') as fout:
    for l in proc(longs):
      short = l.strip(' \r\n')
      if len(short) == 0 or len(short) >= 100:
        continue
      fout.write(short + '\n')

  print('done.')