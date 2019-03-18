#encoding:utf8
import os, sys, re, pdb, codecs
import pickle
import requests
import time
import shutil, hashlib
import json
import progressbar
# from translateAPI import TranslateChinese
from GoogleTranslateAPI import TranslateChinese
bingurl = 'https://speech.platform.bing.com/synthesize'


def GetToken():
    tokenEndpoint = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
    skey = '13682c93e0c147ee89e3408d04d56715'
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Ocp-Apim-Subscription-Key': skey}
    print('POST:', tokenEndpoint)
    content = requests.post(tokenEndpoint, headers = headers)
    with open('token.pkl', 'w') as fout:
        pickle.dump(content, fout)
    print(content.text)
    
def LoadToken():
    with open('token.pkl', 'r') as fin:
        token = pickle.load(fin)
        # print(token.text)
    return token.text


def Synthesize(text,
        appId = '21EC20203AEA1069A2DD08002B30309D',
        clientId = '21EC20203AEA1069A2DD08002B30309D'):
    synthesizeUrl = 'https://speech.platform.bing.com/synthesize'
    token = LoadToken()
    requestData = "<speak version='1.0' xml:lang='en-US'><voice xml:lang='en-US' xml:gender='Female' name='Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)'>{}</voice></speak>".format(text)
    example_requestdata = "<speak version='1.0' xml:lang='en-US'><voice xml:lang='en-US' xml:gender='Female' name='Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)'>Microsoft Bing Voice Output API</voice></speak>"
    # requestData = example_requestdata
    print('request data:', requestData)

    headers = {'User-Agent': 'edream',
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'audio-16khz-64kbitrate-mono-mp3',
            'X-Search-AppId': appId,
            'X-Search-ClientID': clientId,
            'Authorization': 'Bearer {}'.format(token)}
    content = requests.post(synthesizeUrl, headers = headers, data = requestData)
    with open('syn.pkl', 'w') as fout:
        pickle.dump(content, fout)
    if content.status_code != 200:
        print('Error code:', content.status_code)
        print(content.reason)
        return None
    
    return content
    
    

def LoadSynthesisResult():
    with open('syn.pkl', 'r') as fin:
        res = pickle.load(fin)
    print(res)
    print(res.status_code)
    with open('tmp.mp3', 'wb') as fout:
        for chunk in res.iter_content(chunk_size=128):
            fout.write(chunk)
    print('Done')

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
    
def main():
    # LoadToken()
    # GetToken()
    # Synthesize('I want to read a song with a loud voice.')
    # LoadSynthesisResult()
    jsonPath = './v1/dream.json'
    TranslateDreamList(jsonPath, './v1/google_dream.json')
    # SearchImage(jsonPath)
    # TEST_BingImageSearch()
    # print(ParseTextForNewsImageSearch(', it will be a strategic path to keep it ? '''))

    # MakeDreamSpeech(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
