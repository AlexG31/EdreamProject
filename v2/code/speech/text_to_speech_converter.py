#encoding:utf8
import os, sys, re, pdb, codecs
import pickle
import requests
import time
import shutil, hashlib
import json
import progressbar
# from translateAPI import TranslateChinese
#from GoogleTranslateAPI import TranslateChinese
bingurl = 'https://speech.platform.bing.com/synthesize'

def sha(text):
    m = hashlib.sha256()
    m.update(text.encode('utf8'))
    sha_key = m.hexdigest()
    return sha_key

def BatchRun(textList, outputFolder):
    dreamList = []
    for text in textList:
        print('Converting text:', text)
        sha_key = sha(text)
        outputPath = os.path.join(outputFolder, '{}.mp3'.format(sha_key))
        for retry in range(3):
            content = Synthesize(text)
            if content:
                with open(outputPath, 'wb') as fout:
                    for chunk in content.iter_content(chunk_size=128):
                        fout.write(chunk)
                dreamList.append(
                        dict(text = text,
                    speechpath = outputPath))
                break
            # Get auth
            GetToken()
        time.sleep(3)

    jsonPath = os.path.join(outputFolder, 'dream.json')
    with codecs.open(jsonPath,
            'w',
            'utf8') as fout:
        json.dump(dreamList, fout, indent = 4, ensure_ascii = False)
    print('Converted {} lines.'.format(len(dreamList)))
    return jsonPath

def CompressDreamList(jsonPath):
    with codecs.open(jsonPath, 'r', 'utf8') as fin:
        dreamList = json.load(fin)
    hashSet = set()
    dL = []
    for dream in dreamList:
        if dream['speechpath'] in hashSet:
            continue
        hashSet.add(dream['speechpath'])
        dL.append(dream)

    with codecs.open(jsonPath, 'w', 'utf8') as fout:
        json.dump(dL, fout, indent = 4, ensure_ascii = False)
    
    print('Done.')

def BingSearchImage(text):
    imagecount = 10
    subscription_key = 'dc47ed63396f4f40b9a19e587dc57255'
    assert subscription_key
    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
    # search_url = 'https://api.cognitive.microsoft.com/bing/v7.0/images/trending'
    search_term = text
    print(u'Searching image for [{}]'.format(text))

    # Requests
    search_results = ''
    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    params  = {"q": search_term,
            # "license": "Any",
            # "imageType": "photo",
            "cc": "US",
            "count": imagecount,
            "mkt": "en-US",
            "safeSearch": "Moderate"}
    for retry in range(3):
        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 200:
            search_results = response.json()
            if 'value' in search_results:
                print('len value:', len(search_results['value']))
            break
        time.sleep(3)

    return search_results

    
def TranslateDreamList(jsonPath, outPath):
    with codecs.open(jsonPath, 'r', 'utf8') as fin:
        dreamList = json.load(fin)

    # Progress
    bar = progressbar.ProgressBar()
    bar(range(len(dreamList)))
    for ind in range(len(dreamList)):
        bar.next()
        text = dreamList[ind]['text']
        trans_result = TranslateChinese(text)
        dreamList[ind]['chinese'] = trans_result
        time.sleep(3)

    with codecs.open(outPath, 'w', 'utf8') as fout:
        json.dump(dreamList, fout, indent = 4, ensure_ascii = False)
    
    print('Done.')

def SearchImage(jsonPath):
    with codecs.open(jsonPath, 'r', 'utf8') as fin:
        dreamList = json.load(fin)

    # Progress
    bar = progressbar.ProgressBar()
    bar(range(len(dreamList)))
    for ind in range(len(dreamList)):
        bar.next()
        text = dreamList[ind]['text']
        search_term = ParseTextForNewsImageSearch(text)
        resultJson = BingSearchImage(search_term)
        dreamList[ind]['imagejson'] = resultJson
        time.sleep(3)

    with codecs.open(jsonPath, 'w', 'utf8') as fout:
        json.dump(dreamList, fout, indent = 4, ensure_ascii = False)
    
    print('Done.')
    
def MakeDreamSpeech(inPath, outFolder):
    textList = []
    with codecs.open(inPath, 'r', 'utf8') as fin:
        for line in fin:
            line = line.strip()
            textList.append(line)
    jsonPath = BatchRun(textList, outFolder)
    SearchImage(jsonPath)
    # Translate to Chinese
    TranslateDreamList(jsonPath, jsonPath)

def TEST_BingImageSearch():
    # res = BingSearchImage('good path')
    res = BingSearchImage(ParseTextForNewsImageSearch(
        ', it will be a strategic path to keep it ? '''))
    with codecs.open('./text_image_result.json', 'w', 'utf8') as fout:
        json.dump(res, fout, indent = 4, ensure_ascii = False)
            
def LoadWordFrequency():
    worddict = dict()
    with codecs.open('./word_freq.txt', 'r', 'utf8') as fin:
        for line in fin:
            cols = line.strip().split(' ')
            items = filter(lambda x: len(x) > 0, cols)
            worddict[items[1]] = int(items[0])
    return worddict
            
def ParseTextForNewsImageSearch(text, keepnumber = 3):
    invalid_char = re.compile(r'[^a-zA-Z0-9 ]')
    text = invalid_char.sub('', text)
    wordfreq = LoadWordFrequency()
    words = []
    for w in text.split(' '):
        if len(w) > 0:
            if w in wordfreq:
                words.append((w, wordfreq[w]))
            else:
                words.append((w, len(wordfreq) * 2))

    words.sort(key = lambda x:x[1], reverse = True)
    keywords = set([w[0] for w in words[:keepnumber]])
    
    search_term = []
    for w in text.split(' '):
        if len(w) > 0 and w in keywords:
            search_term.append(w)
    
    return u'site:bbc.com ' + u' '.join(search_term)

class Text2SpeechConverter():
    def __init__(self, 
            appId, 
            clientId, 
            tokenOutputPath = './text2speech.token.tmp',
            tokenEndpoint = 'https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken',
            private_key = 'dea851035232423ca91e1c07323174c8',
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

        requestData = "<speak version='1.0' xml:lang='{0}'><voice xml:lang='{0}' xml:gender='Female' name='Microsoft Server Speech Text to Speech Voice ({0}, {2})'>{1}</voice></speak>".format(language,text, speaker)
        #print('request data:', requestData)

        headers = {'User-Agent': 'edream',
                'Content-Type': 'application/ssml+xml',
                'X-Microsoft-OutputFormat': 'audio-16khz-64kbitrate-mono-mp3',
                'Authorization': 'Bearer {}'.format(token)}

        #print('url = ' + url)
        content = requests.post(url, headers = headers, data = requestData)

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
    text2speech = Text2SpeechConverter('', '', tokenEndpoint = 'https://southeastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken', private_key = 'f9ab6cd770f448e983d801f9d37db53d')
    text2speech.getToken()
    text2speech.convert("Jack particularly criticized the Irish government's strategy in the Brexit negotiations", isNeural = True)
    # LoadToken()
    # GetToken()
    # appId = ''
    # clientID = ''
    # Synthesize('I want to read a song with a loud voice.')
    # LoadSynthesisResult()


if __name__ == '__main__':
    main()
