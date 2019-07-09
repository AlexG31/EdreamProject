#encoding:utf8
import os, sys, re, pdb, codecs
import pickle
import requests
import pdb
import time
import shutil, hashlib
import json

import os, requests, uuid, json

# This simple app uses the '/translate' resource to translate text from
# one language to another.

# This sample runs on Python 2.7.x and Python 3.x.
# You may need to install requests and uuid.
# Run: pip install requests uuid

# Checks to see if the Translator Text subscription key is available
# as an environment variable. If you are setting your subscription key as a
# string, then comment these lines out.

def translateV3(text):
    if 'TRANSLATOR_TEXT_KEY' in os.environ:
        subscriptionKey = os.environ['TRANSLATOR_TEXT_KEY']
    else:
        print('Environment variable for TRANSLATOR_TEXT_KEY is not set.')
        exit()
    # If you want to set your subscription key as a string, uncomment the next line.
    #subscriptionKey = 'put_your_key_here'

    # If you encounter any issues with the base_url or path, make sure
    # that you are using the latest endpoint: https://docs.microsoft.com/azure/cognitive-services/translator/reference/v3-0-translate
    base_url = 'https://api.cognitive.microsofttranslator.com'
    path = '/translate?api-version=3.0'
    params = '&to=zh-Hans'
    constructed_url = base_url + path + params

    headers = {
        'Ocp-Apim-Subscription-Key': subscriptionKey,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    # You can pass more than one object in body.
    body = [{
        u'text' : text
    }]
    request = requests.post(constructed_url, headers=headers, json=body)
    response = request.json()

    print(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
    return response[0]["translations"][0]["text"]

def TEST():
    #print(TranslateChinese('how are you?'))
    rs = translateV3('how are you?')
    pdb.set_trace()

def main():
    TEST()

if __name__ == '__main__':
    main()
