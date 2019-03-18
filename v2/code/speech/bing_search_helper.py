#encoding:utf8
import os, sys, re, pdb, codecs
import pickle
import codecs
import requests
import time
import shutil, hashlib
import json
from bing_api_base import BingApiBase
import jieba
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

class BingImageSearcher(BingApiBase):
    def __init__(self, 
            tokenOutputPath = './image-search.token.tmp',
            tokenEndpoint = 'https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken',
            private_key = '37bac983c69046a0bb337f8fefc08ba2',
            service_url = 'https://api.cognitive.microsoft.com/bing/v7.0/images/search'):
        BingApiBase.__init__(self, tokenOutputPath, tokenEndpoint, private_key, service_url)
        self.site_constraint = 'site:(thepaper.cn or chinadaily.com.cn or china.com.cn or chinanews.com or youth.cn or sina.com.cn or xinhuanet.com or cri.cn or 163.com or cankaoxiaoxi.com or cctv.com or ifeng.com or qq.com or takungpao.com or people.com.cn or southcn.com or southcn.com or cnr.cn or people.com.cn or cyol.com or bjnews.com.cn or gmw.cn or dahe.cn or xfrb.com.cn or cqnews.net or lifeweek.com.cn or cpd.com.cn or haiwainet.cn or yidianzixun.com or ftchinese.com or guancha.cn or zhcw.com or huanqiu.com or ihuawen.com or nytimes.com or flickr.com or quanjing.com or vcg.com or gettyimages.co.uk or paixin.com) '
        self.stopwords = set(self.loadStopWords())

    def search(self, text, 
            outputPath = './tmp.mp3',
            language = 'en-US'
        ):
        imagecount = 10
        subscription_key = self.private_key
        assert subscription_key
        search_url = self.service_url
        search_term = self.site_constraint + text
        #print(u'Searching image for' + text)

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
        response = requests.get(search_url, headers=headers, params=params)
        if response.status_code == 200:
            search_results = response.json()
            if 'value' in search_results:
                n = len(search_results['value'])
                return search_results
        return None

    def searchByRule(self, en, zh):
        words = self.stripZh(zh)
        # Search zh
        res = self.search(' '.join(words))
        assert res
        if len(res['value']) > 0:
            return res
        # Search en
        res = self.search(en)
        assert res
        if len(res['value']) > 0:
            return res

        # Search 3 words zh
        res = self.search(' '.join(words[:3]))
        assert res
        if len(res['value']) > 0:
            return res
        return None
        
        

    def loadStopWords(self, in_path = r'zh-stopwords.txt'):
        lines = []
        with codecs.open(in_path, 'r', 'utf8') as fin:
            for line in fin:
                lines.append(line.strip('\r\n'))
        return lines
    def stripZh(self, text):
        stopwords = self.stopwords
        words = []
        for it in jieba.cut(text):
            if it in stopwords:
                continue
            words.append(it)
                
        return words
        
def main():
    img = BingImageSearcher()
    print(img.tokenOutputPath)
    text = u'杰克特别批评爱尔兰政府在英国退欧谈判中的策略，'
    img.searchByRule(text, text)
    #res = img.search()
    # LoadToken()
    # GetToken()
    # appId = ''
    # clientID = ''
    # Synthesize('I want to read a song with a loud voice.')
    # LoadSynthesisResult()


if __name__ == '__main__':
    main()
