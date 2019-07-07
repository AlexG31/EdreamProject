import glob, sys, os
import re
import pdb
import logging

copyright_pattern = re.compile(r'^[\s]*copyright')
space_pattern = re.compile(r'[\s]+')

def read_news(in_path):
  clog = logging.getLogger('data.merger')
  contents = []
  with open(in_path) as fin:
    fin.readline()
    for line in fin:
      line = space_pattern.sub(' ', line).strip(' \r\n')
      if len(line) == 0 or len(line.split(' ')) < 10:
        continue
      contents.append(line)

  # Filter contents
  n = len(contents)
  if n > 0 and copyright_pattern.match(contents[n - 1].lower()):
     n -= 1
  elif n > 0:
    c = contents[-1]
    c = space_pattern.sub('', c)
    if len(c) > 0:
      clog.info(in_path)
      clog.info(contents[-1])
  if n < 3:
    n = 0

  return contents[:n]

def merge_news(in_folder, out_path):
  clog = logging.getLogger('data.merger')
  raw_htmls = glob.glob(os.path.join(in_folder, '**', '*.html'), recursive=True)
  clog.info('Total number of raw htmls: {}'.format(len(raw_htmls)))
  fout = open(out_path, 'w')

  for p in raw_htmls:
    contents = read_news(p)
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

  print('done')