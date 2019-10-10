#encoding:utf8
import os, sys
import json
import argparse
import pdb
from decode_and_split_long_lines import proc

pron = set([
  'I',
  'we',
  'our',
  'you',
  'your'
])
says = set([
  'said',
  'say',
  'says'
])

def shornplain(line):
  words = line.split(' ')
  hasPron = False
  hasSays = checkHasSays(line)
  for w in words:
    if w in pron:
      hasPron = True

  if hasPron and not hasSays:
    return True
  else:
    return False

def checkHasSays(line):
  hasSays = False
  for s in says:
    if -1 != line.find(s):
      hasSays = True
  return hasSays


def filterShortPlainLines(lines):
  result = []
  n = len(lines)
  for ind, line in enumerate(lines):
    if shornplain(line):
      if ind + 1 >= n or checkHasSays(lines[ind + 1]) == False:
        result.append(line)

  return result



def splitAll(lines):
  results = []
  for l in proc(lines):
    short = l.strip(' \r\n')
    if len(short) == 0 or len(short) >= 100:
      continue
    results.append(short)
  return results

def manualStoryRules(lines):
  lines = splitAll(lines)
  lines = filterShortPlainLines(lines)
  return lines

if __name__ == '__main__':
  psr = argparse.ArgumentParser()
  psr.add_argument('-in', type=str, help = 'in')
  psr.add_argument('-out', type=str, help = 'out')
  input_args = vars(psr.parse_args())

  in_path = input_args['in']
  out_path = input_args['out']

  with open(in_path, 'r') as fin:
    data = json.load(fin)

  lines = [x[0] for x in data]
  lines = manualStoryRules(lines)
  cnt = 0
  with open(out_path, 'w', encoding='utf8') as fout:
    for l in lines:
      cnt += 1
      fout.write(l + '\n')

  print('total {} shortplain lines'.format(cnt))
  print('done.')