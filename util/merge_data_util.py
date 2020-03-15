#encoding:utf8
import glob, sys, os
import re
import pdb
import logging

copyright_pattern = re.compile(r'^[\s]*copyright')
space_pattern = re.compile(r'[\s]+')

illegalChars = [u'é', u'ú', u'ç', u'ã', u'ó', ]
def judgeIllegalCharacter(line):
  for c in illegalChars:
    if line.find(c) != -1:
      return False
  return True

n_cur = 0
def judgeScriptLength(line, min_len = 5, max_len = 20000):
  global n_cur
  N = len(line.split(' '))
  if N > n_cur:
    n_cur = N
  return N > min_len and N <= max_len

endingPattern = re.compile(r'[^a-z0-9A-Z]$')
def judgeEnding(line):
    return endingPattern.search(line) != None

repeatMem = set()
def filterTrainingData(lines):
  global repeatMem
  result = list()
  for line in lines:
    if line not in repeatMem and judgeEnding(line) and judgeScriptLength(line) and judgeIllegalCharacter(line):
      result.append(line)
      repeatMem.add(line)
  return result

def splitLine(line):
    quotes = [
        u'""',
        u'“”'
    ]
    stops = set([
        '.',
        ',',
        '，',
        '。',
        '!',
        '?',
        ';'
        ])
    results = []
    cur = ''
    prev_quote = None
    for c in line:
        ch = c
        if prev_quote is not None:
            if c == quotes[prev_quote][1] and judgeScriptLength(cur):
                cur += c
                results.append(cur)
                cur = ''
                prev_quote = None
                ch = ''
        else:
            if c in stops and judgeScriptLength(cur):
                cur += c 
                results.append(cur)
                cur = ''
                ch = ''
            
        cur += ch
        for ind in range(len(quotes)):
            if quotes[ind][0] == ch:
                prev_quote = ind
                break
    if judgeScriptLength(cur):
        results.append(cur)
    return results

def read_news(in_path):
  clog = logging.getLogger('data.merger')
  contents = []
  with open(in_path, 'r', encoding='utf8') as fin:
    fin.readline()
    for line in fin:
      line = space_pattern.sub(' ', line).strip(' \r\n')
      if len(line.split(' ')) <= 0:
        continue
      contents.append(line)

  # Filter contents
  n = len(contents)
  if n > 0 and copyright_pattern.match(contents[n - 1].lower()):
     n -= 1
  if n < 3:
    n = 0

  return contents[:n]

def merge_news(in_folder, out_path):
  clog = logging.getLogger('data.merger')
  raw_htmls = glob.glob(os.path.join(in_folder, '**', '*.html'), recursive=True)
  clog.info('Total number of raw htmls: {}'.format(len(raw_htmls)))
  fout = open(out_path, 'w', encoding='utf8')

  for p in raw_htmls:
    contents = read_news(p)
    contents = filterTrainingData(contents)
    fout.writelines([x + '\n' for x in contents])
  
  fout.close()

if __name__ == '__main__':
  # crawler logger
  #logging.basicConfig(
  #    filename = os.path.join('./', 'merge.log'),
  #    level = 'INFO')
  #base_folder = '/media/alexg/vol1/data/news/2019-06-23/'
  #out_file = './out.html'
  in_folder = sys.argv[1]
  out_file = sys.argv[2]
  merge_news(in_folder, out_file)
  print('max words per line:', n_cur)

  print('done')
