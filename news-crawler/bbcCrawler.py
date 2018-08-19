import os, sys, re, pdb
import codecs, time
import random
from newspaper import Article
import newspaper
from newspaper.configuration import Configuration
from multiprocessing.dummy import Pool as ThreadPool
import wget

debug = False
OutputFolder = None
RawHtmlFolder = None
def url2Filename(url):
    pattern = re.compile(r'[^0-9a-zA-Z_]')
    filename = pattern.sub('_', url)
    return filename

def ReloadSource(cnn_paper, url):
    outPath = os.path.join(RawHtmlFolder, '{}.txt'.format(url2Filename(url)))
    wget.download(url, out = outPath)
    html = ''
    with codecs.open(outPath, 'r', 'utf8') as fin:
        for line in fin:
            html += line

    # Reload source
    cnn_paper.html = html
    cnn_paper.parse()

    cnn_paper.set_categories()
    cnn_paper.download_categories()  # mthread
    cnn_paper.parse_categories()

    cnn_paper.set_feeds()
    cnn_paper.download_feeds()  # mthread

    cnn_paper.generate_articles()

    print('Reload {}, [{}] articles.'.format(url, len(cnn_paper.articles)))
    return cnn_paper

    
def collectNews(url):

    time.sleep(random.randint(2,10))
    newsConf = Configuration()
    newsConf.request_timeout = 10
    # newsConf.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
    cnn_paper = newspaper.build(url, conf = newsConf)
    print('Collecting news from {}, [{}] articles.'.format(url, len(cnn_paper.articles)))
    # if len(cnn_paper.articles) == 0:
        # cnn_paper = ReloadSource(cnn_paper, url)
    if debug and len(cnn_paper.articles) == 0:
        logPath = '/home/alex/log/{}.html'.format(
            url2Filename(cnn_paper.url))
        with codecs.open(logPath, 'w', 'utf8') as fout:
            fout.write(cnn_paper.html)
            print('Debug: base html written to {}'.format(logPath))
    
    for cnn_article in cnn_paper.articles:
        outPath = os.path.join(OutputFolder,
                '{}/{}.txt'.format(GetTimestampDirName(),
                    url2Filename(cnn_article.url)))
        if os.path.exists(os.path.dirname(outPath)) == False:
            os.mkdir(os.path.dirname(outPath))

        if os.path.exists(outPath):
            continue
        cnn_article.download()
        time.sleep(random.randint(2,10))
        try:
            cnn_article.parse()
        except Exception:
            print('Skip not downloaded...')
            continue

        with codecs.open(outPath, 'w', 'utf8') as fout:
            fout.write(cnn_article.text)
            
        print('Parsed {}.'.format(cnn_article.url))


# global folder name, init once
g_TimestampFolderName = None
def GetTimestampDirName():
    return g_TimestampFolderName
    # return time.strftime('%Y%m%d') + '_{}'.format(int(time.time()))

def GetDate():
    return time.strftime('%Y%m%d')
    
def CrawUrlList(InPath, ThreadPoolSize, OutputFolder):
    pool = ThreadPool(ThreadPoolSize)
    urls = list()
    with codecs.open(InPath, 'r', 'utf8') as fin:
        for line in fin:
            url = line.strip('\r\n ')
            urls.append(url)

    pool.map(collectNews, urls)
    pool.close()
    pool.join()
            

if __name__ == '__main__':
    # parse()
    # collectCnnNews()
    # collectNews(sys.argv[1])
    
    OutputFolder = sys.argv[2]
    if os.path.exists(OutputFolder) == None:
        raise Exception('OutputFolder not exist!')
    RawHtmlFolder = sys.argv[3]
    if os.path.exists(RawHtmlFolder) == None:
        raise Exception('RawHtmlFolder not exist!')
    g_TimestampFolderName = time.strftime('%Y%m%d') + '_{}'.format(int(time.time()))
    timestampFolder = os.path.join(OutputFolder, GetTimestampDirName())
    if os.path.exists(timestampFolder) == False:
        os.mkdir(timestampFolder)

    ThreadPoolSize = 5
    if len(sys.argv) > 4:
        ThreadPoolSize = int(sys.argv[4])
    CrawUrlList(sys.argv[1], ThreadPoolSize, OutputFolder)
