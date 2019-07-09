#encoding:utf8
import os, sys, re, pdb, codecs
import pickle
import requests
import time
import shutil, hashlib
import json


result_pat = re.compile(r'<[^>]+>(.*)</string>')

def TranslateChinese(text, target = 'zh-Hans'):
    subkey = '4d71d02286a54a0da93ff93a3dbf5396'
    # host = 'api.microsofttranslator.com'
    urlpath = 'https://api.microsofttranslator.com/V2/Http.svc/Translate'

    payload = {'to': target, 'text': text}

    headers = {'Ocp-Apim-Subscription-Key': subkey}
    response = requests.get(urlpath, params=payload, headers = headers)

    result = response.text
    print(result)
    trans_text = result_pat.search(result)
    if trans_text:
        return trans_text.group(1)
    return ''



def TEST_Translate():
    print(TranslateChinese('how are you?'))

def main():
    TEST_Translate()


if __name__ == '__main__':
    main()
