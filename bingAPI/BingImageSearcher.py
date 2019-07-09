#encoding:utf8
import os, sys, re, pdb, codecs, random
import pickle
import codecs
import requests
import time
import shutil, hashlib
import json
from BingApiBase import BingApiBase
import jieba
# from translateAPI import TranslateChinese
#from GoogleTranslateAPI import TranslateChinese
bingurl = 'https://speech.platform.bing.com/synthesize'

class BingImageSearcher(BingApiBase):
    def __init__(self, 
            stop_words,
            tokenOutputPath = './image-search.token.tmp',
            tokenEndpoint = 'https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issueToken',
            private_key = '',
            service_url = 'https://api.cognitive.microsoft.com/bing/v7.0/images/search'):
        BingApiBase.__init__(self, tokenOutputPath, tokenEndpoint, private_key, service_url)
        self.site_constraint = 'site:(thepaper.cn or chinadaily.com.cn or china.com.cn or chinanews.com or youth.cn or sina.com.cn or xinhuanet.com or cri.cn or 163.com or cankaoxiaoxi.com or cctv.com or ifeng.com or qq.com or takungpao.com or people.com.cn or southcn.com or southcn.com or cnr.cn or people.com.cn or cyol.com or bjnews.com.cn or gmw.cn or dahe.cn or xfrb.com.cn or cqnews.net or lifeweek.com.cn or cpd.com.cn or haiwainet.cn or yidianzixun.com or ftchinese.com or guancha.cn or zhcw.com or huanqiu.com or ihuawen.com or nytimes.com or flickr.com or quanjing.com or vcg.com or gettyimages.co.uk or paixin.com) '
        self.stopwords = set(stop_words)

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
        zh_terms = ' '.join(words[:7])
        print('zh search terms:', zh_terms)
        res = self.search(zh_terms)
        assert res
        if len(res['value']) > 0:
            return res
        # Search en
        en_terms = self.stripEn(en)
        print('en search terms:', en_terms)
        res = self.search(en_terms)
        assert res
        if len(res['value']) > 0:
            return res

        # Search 3 words zh
        zh_terms = ' '.join(random.sample(words, 3))
        print('zh search terms:', zh_terms)
        res = self.search(zh_terms)
        assert res
        if len(res['value']) > 0:
            return res
        else:
            print('no search response:', res)
            return None
        

    def stripEn(self, text):
        terms = []
        pat = re.compile(r'[^a-zA-Z]')
        for w in text.split(' '):
            if w.lower() in self.stopwords:
                continue
            if pat.search(w) is not None or len(w) <= 0:
                continue
            terms.append(w.lower())
        return ' '.join(terms)

    def stripZh(self, text):
        stopwords = self.stopwords
        words = []
        for it in jieba.cut(text):
            if it in stopwords:
                continue
            words.append(it)
                
        return words
        
def loadStopWords(in_path = r'zh-stopwords.txt'):
    lines = []
    with codecs.open(in_path, 'r', 'utf8') as fin:
        for line in fin:
            lines.append(line.strip('\r\n'))
    return lines

def main():
    img = BingImageSearcher(loadStopWords())
    print(img.tokenOutputPath)
    text = u'杰克特别批评爱尔兰政府在英国退欧谈判中的策略，'
    img.searchByRule(text, text)

if __name__ == '__main__':
    main()
