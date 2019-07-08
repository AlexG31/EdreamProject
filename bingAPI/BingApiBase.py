#encoding:utf8
import os, sys, re, pdb, codecs
import pickle
import requests
import time
import shutil, hashlib
import json

class BingApiBase():
    def __init__(self, 
            tokenOutputPath = './bingapi.token.tmp',
            tokenEndpoint = 'https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken',
            private_key = '',
            service_url = 'https://eastasia.tts.speech.microsoft.com/cognitiveservices/v1'):
        self.service_url = service_url
        self.private_key = private_key
        self.tokenEndpoint = tokenEndpoint
        self.tokenOutputPath = tokenOutputPath

    def getToken(self):
        headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
                'Ocp-Apim-Subscription-Key': self.private_key}
        print('POST:', self.tokenEndpoint)
        content = requests.post(self.tokenEndpoint, headers = headers)
        with open(self.tokenOutputPath, 'w') as fout:
            pickle.dump(content, fout)
        print('==== token ====')
        print(content.text)
        
    def loadToken(self):
        with open(self.tokenOutputPath, 'r') as fin:
            token = pickle.load(fin)
        return token.text

        
def main():
    pass

if __name__ == '__main__':
    main()
