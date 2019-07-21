#encoding:utf8
import os, sys
import json, re
import argparse
import pdb

class SentenceDuplicateDetector:
  def __init__(self):
    self.lines = []
    self.word_regex = re.compile(r'([a-zA-Z]+)')

  def ingest(self, sentence):
    self.lines.append(sentence)

  def isDuplicateBrute(self, sentence):
    for l in self.lines:
      r = self.overlapRatio(sentence, l)
      if r > 0.6 + 1e-6:
        #print('[{}] dup with [{}]'.format(sentence, l))
        return True
    return False

  def splitWords(self, sentence):
    words = self.word_regex.findall(sentence)
    #print('{}\n{}\n'.format(sentence, words))
    return words

  def overlapRatio(self, source, target):
    source_words = dict()
    n = 0
    for w in self.splitWords(source):
      if w not in source_words:
        source_words[w] = 0
      source_words[w] += 1
      n += 1

    if n == 0:
      return 1.0

    cnt = 0
    for w in self.splitWords(target):
      remain = source_words.get(w, 0)
      if remain > 0:
        source_words[w] -= 1
        cnt += 1

    return float(cnt) / n
    
def getDuplicate(data):
  detector = SentenceDuplicateDetector()
  dups = []
  line_index = -1
  for en, zh, line_hash in data:
    line_index += 1
    if (detector.isDuplicateBrute(en)):
      dups.append(en)
      print('[{}]dup: '.format(line_index), en)
      #pdb.set_trace()
    detector.ingest(en)

  return dups
    
if __name__ == '__main__':
  psr = argparse.ArgumentParser()
  psr.add_argument('-json_path', nargs = 1, help = 'json file to send')
  psr.add_argument('-out', nargs = 1, help = 'output file')
  input_args = vars(psr.parse_args())

  json_path = input_args['json_path'][0]
  out_path = input_args['out'][0]
  print('input json path:', json_path)

  with open(json_path, 'r', encoding='utf8') as fin:
    data = json.load(fin)
    
  n = len(data)
  dup = getDuplicate(data)
  print('dup lines:', len(dup))
  print('duplicate ratio: {:.2f}%'.format(len(dup) / float(n) * 100.0))
  #pdb.set_trace()