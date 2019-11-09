#encoding:utf8
import os, sys
import json
import argparse
import random
import pdb
from decode_and_split_long_lines import proc

pron = set([
  'i',
  'we',
  'our',
  'you',
  'your'
])
says = set([
  'said',
  'say',
  'says',
  'add',
  'adds',
  'added',
  'tell',
  'tells',
  'told',
  'continue',
  'continues',
  'continued',
  'argue',
  'argues',
  'argued',
  'point out',
  'pointed out',
  'points out'
])

def shornplain(line):
  lower_line = line.lower()
  words = lower_line.split(' ')
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
  lower_line = line.lower()
  hasSays = False
  for s in says:
    if -1 != lower_line.find(s):
      hasSays = True
  return hasSays

def appendHeSays(line):
  def generateTail():
    names = ['Jack', 'Rose']
    actions = ['said', 'added', 'continued', 'pointed out', 'cried', 'smiled', 'laughed']
    return names[random.randint(0, len(names) - 1)] + ' ' + \
      actions[random.randint(0, len(actions) - 1)]
  def generate(proba = 0.1):
    tails = ['Jack told Rose', 'Rose told Jack']
    if random.random() < proba:
      return tails[random.randint(0, 1)]
    else:
      return generateTail()

  return line + ' ' + generate() + '.'

def filterShortPlainLines(lines):
  result = []
  n = len(lines)
  for ind, line in enumerate(lines):
    if shornplain(line):
      line = appendHeSays(line)
      result.append(line)
    else:
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