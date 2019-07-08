#encoding:utf8

# Imports the Google Cloud client library
from translateAPI import TranslateChinese
import re
import sys
import codecs

def judgeScriptLength(line, min_len = 5):
    return len(line.split(' ')) > min_len

endingPattern = re.compile(r'[^a-z0-9A-Z]$')
def judgeEnding(line):
    return endingPattern.search(line) != None

def getLines(path):
    results = []
    with open(path, 'r') as fin:
        for line in fin:
            ct = line.strip(' \r\n')
            if len(ct) > 0 and judgeEnding(ct) and judgeScriptLength(ct):
                results.append(ct)
    return results
            
if __name__ == '__main__':
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    print('input path: ', in_path)
    print('output path: ', out_path)
    results = getLines(in_path)
    fout = codecs.open(out_path, 'w', "utf8")
    for line in results:
        tr = TranslateChinese(line)
        print(tr)
        #tr = u"[{}]".format(line.decode('utf8'))
        fout.write(u'\t'.join([line.decode('utf8'), tr]))
        fout.write('\n')
        

    fout.close()