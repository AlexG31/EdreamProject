#encoding:utf8
import os, sys, re, pdb, codecs
import pickle
import codecs
import requests
import time
import shutil, hashlib
import json
from BingImageSearcher import BingImageSearcher, loadStopWords

def batchImage(lines, save_folder, private_key, stop_words):
    N = len(lines)
    print('== Total {} =='.format(len(lines)))

    img = BingImageSearcher(stop_words, private_key=private_key)
    
    ind = N
    empty_count = 0
    for en, zh, en_hash in lines:
        print('{} lines left.'.format(ind))
        ind -= 1

        # Format output path
        name = en_hash
        output_path = save_folder + name + '.json'
        if os.path.exists(output_path):
            continue
        #print(output_path)
        content = img.searchByRule(en, zh)
        if content is None:
            empty_count += 1
        
        with codecs.open(output_path, 'w', 'utf8') as fout:
            json.dump(content, fout, indent = 4, ensure_ascii = False)
        
        time.sleep(5.5)
    print('Error count: {}'.format(empty_count))
 
def getPrivateKey():
    if 'IMAGE_PRIVATE_KEY' in os.environ:
        subscriptionKey = os.environ['IMAGE_PRIVATE_KEY']
        return subscriptionKey
    else:
        print('Environment variable for TRANSLATOR_TEXT_KEY is not set.')
        exit()

def loadLines(in_path):
    with codecs.open(in_path, 'r', 'utf8') as fin:
        data = json.load(fin)

    return data

def main():
    in_file = sys.argv[1]
    save_folder = sys.argv[2]
    stop_word_file = sys.argv[3]
    stop_words = loadStopWords(in_path = stop_word_file)
    private_key = getPrivateKey()
    lines = loadLines(in_file)
    batchImage(lines, save_folder, private_key, stop_words)

if __name__ == '__main__':
    main()
