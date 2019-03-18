#encoding:utf8
import os, sys, re, pdb, codecs
import pickle
import codecs
import requests
import time
import shutil, hashlib
import json
from bing_api_base import BingApiBase
from text_to_speech_converter import sha
from bing_search_helper import BingImageSearcher
from util import loadLines


def batchImage(save_folder):
    lines = loadLines()
    N = len(lines)
    print('== Total {} =='.format(len(lines)))

    img = BingImageSearcher()
    
    ind = N
    empty_count = 0
    for en, zh in lines:
        print('{} lines left.'.format(ind))
        ind -= 1

        # Format output path
        name = sha(en.decode('utf8'))
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
    
 

def main():
    save_folder = '/Users/AlexG/Documents/2019/E-Dream/2019.03/image-json/'
    batchImage(save_folder)
    

if __name__ == '__main__':
    main()
