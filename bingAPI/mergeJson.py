#encoding:utf8

# Imports the Google Cloud client library
import re
import json
import sys
import codecs
import shutil, hashlib
import base64
import time, os


if __name__ == '__main__':
    history_path = sys.argv[1]
    in_path = sys.argv[2]
    out_path = sys.argv[3]
    print('history path: ', history_path)
    print('input path: ', in_path)
    print('output path: ', out_path)

    with codecs.open(history_path, 'r', 'utf8') as fin:
        data = json.load(fin)

    with codecs.open(in_path, 'r', 'utf8') as fin:
        new_data = json.load(fin)

    data.extend(new_data)

    with codecs.open(out_path, 'w', 'utf8') as fout:
        json.dump(data, fout, indent=4, ensure_ascii=False)