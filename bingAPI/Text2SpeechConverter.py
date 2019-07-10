#encoding:utf8
import os, sys, re, pdb, codecs
import pickle
import requests
import time
import shutil, hashlib
import json
# from translateAPI import TranslateChinese
#from GoogleTranslateAPI import TranslateChinese
bingurl = 'https://speech.platform.bing.com/synthesize'

def sha(text):
    m = hashlib.sha256()
    m.update(text.encode('utf8'))
    sha_key = m.hexdigest()
    return sha_key

class Text2SpeechConverter():
    def __init__(self, 
            appId, 
            clientId, 
            tokenOutputPath = './text2speech.token.tmp',
            tokenEndpoint = 'https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken',
            private_key = '',
            synthesizeUrl = 'https://eastasia.tts.speech.microsoft.com/cognitiveservices/v1'):
        self.appId = appId
        self.clientId = clientId
        self.synthesizeUrl = synthesizeUrl
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

    def convert(self, text, 
            outputPath = './tmp.mp3',
            language = 'en-US',
            isNeural = False
            ):
        #print('Text to convert: {}'.format(text))
        token = self.loadToken()
        speaker = 'ZiraRUS'
        url = self.synthesizeUrl
        if isNeural:
            speaker = 'JessaNeural'
            url = 'https://southeastasia.tts.speech.microsoft.com/cognitiveservices/v1'
        # Add language parameters
        url = url + '?language={}'.format(language)

        requestData = u"<speak version='1.0' xml:lang='{0}'><voice xml:lang='{0}' xml:gender='Female' name='Microsoft Server Speech Text to Speech Voice ({0}, {2})'>{1}</voice></speak>".format(language,text, speaker)
        #print('request data:', requestData)

        headers = {'User-Agent': 'edream',
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': 'audio-16khz-64kbitrate-mono-mp3',
                'Authorization': 'Bearer {}'.format(token)}

        #print('url = ' + url)
        content = requests.post(url, headers = headers, data = requestData.encode('utf8'))

        if content.status_code != 200:
            print('Error code:', content.status_code)
            print(content.reason)
            return None

        with open(outputPath, 'wb') as fout:
            for chunk in content.iter_content(chunk_size=128):
                fout.write(chunk)
            #print(u'mp3 file output to ' + outputPath)
        
        return content
        
def main():
    text2speech = Text2SpeechConverter('', '', tokenEndpoint = 'https://southeastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken', private_key = '')
    text2speech.getToken()
    text2speech.convert("Jack particularly criticized the Irish government's strategy in the Brexit negotiations", isNeural = True)

if __name__ == '__main__':
    main()