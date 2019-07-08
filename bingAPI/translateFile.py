#encoding:utf8

# Imports the Google Cloud client library
from translateAPI import translateV3
import re
import json
import sys
import codecs
import shutil, hashlib
import base64
import time, os

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
            

def sha(text):
    m = hashlib.sha256()
    m.update(text.encode('utf8'))
    sha_key = m.hexdigest()
    return sha_key

def generateScriptJson(lines, outputPath):
    with codecs.open(outputPath, 'w', 'utf8') as fout:
        json.dump(lines, fout, indent = 4, ensure_ascii = False)

if __name__ == '__main__':
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    print('input path: ', in_path)
    print('output path: ', out_path)

    lines = getLines(in_path)
    results = []
    for line in lines:
        line = line.decode('utf8')
        tr = translateV3(line)
        print(tr)
        #tr = u"[{}]".format(line.decode('utf8'))
        results.append([line, tr, sha(line)])

    generateScriptJson(results, out_path)