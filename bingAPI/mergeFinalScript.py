#encoding:utf8

# Imports the Google Cloud client library
import re
import json
import sys
import codecs
import shutil, hashlib
import base64
import time, os
import random

def judgeScriptLength(line, min_len = 5, max_len = 18):
    N = len(line.split(' '))
    return N >= min_len and N <= max_len

endingPattern = re.compile(r'[^a-z0-9A-Z]$')
def judgeEnding(line):
    return endingPattern.search(line) != None

def getLines(path):
    results = []
    with codecs.open(path, 'r', 'utf8') as fin:
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

replaceMap = [
    (re.compile(r"\b[Ss]he\b"), "Rose"),
    (re.compile(r"\b[Hh]er\b"), "Rose"),
    (re.compile(r"\b[Hh]e\b"), "Jack"),
    (re.compile(r"\b[Hh]im\b"), "Jack"),
]
def randomReplaceJackRose(line, replace_proba = 0.3):
    replace_count = 0
    src = line
    for pat, token in replaceMap:
        search_result = pat.search(src)
        if search_result is not None:
            if random.random() <= replace_proba:
                src = src[:search_result.start()] + token + src[search_result.end():]
                replace_count += 1

    if replace_count > 0:
        print('Total replace jack/rose:', replace_count)
    return src

if __name__ == '__main__':
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    history_path = sys.argv[3]
    print('input path: ', in_path)
    print('output path: ', out_path)
    print('history path: ', history_path)

    history_lines = set()
    with codecs.open(history_path, 'r', 'utf8') as fin:
        data = json.load(fin)
        for en, zh, h in data:
            history_lines.add(sha(en))
    lines = getLines(in_path)

    fout = codecs.open(out_path, 'w', 'utf8')
    for line in lines:
        h = sha(line)
        if h in history_lines:
            continue
        history_lines.add(h)
        line = randomReplaceJackRose(line)
        fout.write(line)
        fout.write('\n')

    fout.close()