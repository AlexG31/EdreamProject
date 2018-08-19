#encoding:utf8
import os, sys, codecs, re, pdb
import glob, time
import shutil, hashlib
import collections

def ProcessStats(dataFolderPattern, destFolder):
    dataFolders = glob.glob(dataFolderPattern)
    que = collections.deque(dataFolders)
    total = 0
    totalSize = 0
    while len(que) > 0:
        path = que.popleft()
        if os.path.isdir(path):
            print('dir:', path)
            que.extend(glob.glob(os.path.join(path, '*')))
        else:
            if path.endswith('.txt') == False:
                continue
            filesize = os.path.getsize(path)
            total += 1
            totalSize += filesize

            if filesize > 10:
                # 10 Byte
                destPath = os.path.join(destFolder, os.path.split(path)[-1])
                if os.path.exists(destPath):
                    continue
                shutil.copyfile(path, destPath)
            # print(path)
            # pdb.set_trace()

    print('Total {} files, {} MB.'.format(total, totalSize / 1024.0 / 1024.0))

def FilterLines(inFolder, destFolder):
    '''1. Hash each line.
       2. Remove wordcount(line) < 10
       3. Remove single line file.
       '''
    # destFolder = './training/filter20180324c/'
    WordThreshold = 9
    LineThreshold = 1
    newsPathList = glob.glob(os.path.join(inFolder, '*.txt'))
    
    lineHashSet = set()
    for path in newsPathList:
        lineCnt = 0
        outPath = os.path.join(destFolder, os.path.split(path)[-1])
        if os.path.exists(outPath):
            continue
        fout = codecs.open(outPath, 'w', 'utf8')
        with codecs.open(path, 'r', 'utf8') as fin:
            for line in fin:
                words = line.strip('\r\n ').split(' ')
                if len(words) <= WordThreshold:
                    continue

                # Hash
                m = hashlib.sha256()
                m.update(line.encode('utf8'))
                sha_key = m.hexdigest()
                if sha_key in lineHashSet:
                    continue
                lineHashSet.add(sha_key)

                # Output
                if re.search(r'[a-zA-Z]+', line) is not None:
                    lineCnt += 1
                else:
                    continue
                fout.write(line)
            
        fout.close()
        if lineCnt <= LineThreshold:
            os.remove(outPath)
            continue
        if os.path.getsize(outPath) == 0:
            print('LineCnt:', lineCnt)
            print(outPath)
            pdb.set_trace()
        # shutil.copy(path, os.path.join(destFolder, os.path.split(path)[-1]))

def FilterNoNews(inFolder):
    destFolder = './training/filter20180323b/'
    WordThreshold = 10
    LineThreshold = 1
    newsPathList = glob.glob(os.path.join(inFolder, '*.txt'))
    
    contentHashSet = set()
    for path in newsPathList:
        lineCnt = 0
        wordCnt = 0
        with codecs.open(path, 'r', 'utf8') as fin:
            content = ''
            for line in fin:
                content += line
                lineCnt += 1
                words = line.strip('\r\n ').split(' ')
                wordCnt += len(words)
            m = hashlib.sha256()
            m.update(content.encode('utf8'))
            sha_key = m.hexdigest()
            if sha_key in contentHashSet:
                print('Duplicate content:', path)
                continue
            contentHashSet.add(sha_key)
            
        if lineCnt <= LineThreshold or wordCnt <= WordThreshold:
            continue
        shutil.copy(path, os.path.join(destFolder, os.path.split(path)[-1]))

def CountLines(inFolder):
    total = 0
    LineCountList = list()
    sourceList = glob.glob(os.path.join(inFolder, '*.txt'))
    for path in sourceList:
        lineCnt = 0
        with codecs.open(path, 'r', 'utf8') as fin:
            for line in fin:
                lineCnt += 1
        LineCountList.append(lineCnt)

    total = sum(LineCountList)
    print('==LineCount==')
    print(total)
    print('==Max lines in a file==')
    print(max(LineCountList))
    


def MergeRawText(inFolder, outPath, SplitCommaWordCountThreshold = 38,
        MergeLineWordCountThreshold = 9):
    sourceList = glob.glob(os.path.join(inFolder, '*.txt'))
    fout = codecs.open(outPath, 'w', 'utf8')
    outputLineCount = 0
    fileIndex = 0
    
    quotePairs = [u'""',
            u'()',
            u'[]',
            u'{}',
            u'“”',
            ]
    left_quotes = set([x[0] for x in quotePairs])
    left_quote_of = dict()
    right_quotes = set([x[1] for x in quotePairs])
    for q in quotePairs:
        left_quote_of[q[1]] = q[0]

    for path in sourceList:
        fileIndex += 1
        if fileIndex % 200 == 0:
            print('{} files loaded.'.format(fileIndex))
        with codecs.open(path, 'r', 'utf8') as fin:
            for line in fin:
                fout.write(line)
    fout.close()

def SplitLines(inFolder, outPath, SplitCommaWordCountThreshold = 38,
        MergeLineWordCountThreshold = 9):
    sourceList = glob.glob(os.path.join(inFolder, '*.txt'))
    fout = codecs.open(outPath, 'w', 'utf8')
    outputLineCount = 0
    fileIndex = 0
    
    quotePairs = [u'""',
            u'()',
            u'[]',
            u'{}',
            u'“”',
            ]
    left_quotes = set([x[0] for x in quotePairs])
    left_quote_of = dict()
    right_quotes = set([x[1] for x in quotePairs])
    for q in quotePairs:
        left_quote_of[q[1]] = q[0]

    for path in sourceList:
        fileIndex += 1
        if fileIndex % 200 == 0:
            print('{} files loaded.'.format(fileIndex))
        with codecs.open(path, 'r', 'utf8') as fin:
            for line in fin:
                short_lines = [sl.strip() for sl in 
                        line.strip('\r\n ').split('.')]
                # Split Long Lines
                ss_lines = list()
                for sl in short_lines:
                    ss_lines.extend([x.strip() for x in sl.split(',')])
                # for sl in short_lines:
                    # if len(sl.split(' ')) > SplitCommaWordCountThreshold:
                        # ss_lines.extend(sl.split(','))
                    # else:
                        # ss_lines.append(sl)
                # Merge short lines
                short_lines = list()
                last_line = ''
                
                quote_stack = collections.deque()
                for sl in ss_lines:
                    if len(sl.split(' ')) <= MergeLineWordCountThreshold:
                        last_line += sl
                    else:
                        if (len(last_line) > 0 and
                                len(last_line.split(' ')) > MergeLineWordCountThreshold and
                                len(quote_stack) == 0):
                            short_lines.append(last_line)
                            last_line = ''
                        last_line += sl
                    for ch in sl:
                        if ch in right_quotes:
                            if len(quote_stack) > 0 and quote_stack[-1] == left_quote_of[ch]:
                                quote_stack.pop()
                        elif ch in left_quotes:
                            quote_stack.append(ch)
                    # print(sl)
                    # print(quote_stack)
                if len(last_line) > 0:
                    short_lines.append(last_line)
                    
                for sl in short_lines:
                    sl = sl.strip()
                    if len(sl) == 0:
                        continue
                    if sl[-1].isalpha():
                        sl += '.'
                    # if len(sl.split(' ')) > 40:
                        # print(u'[{},{}]{}'.format(len(sl.split(' ')), len(sl), sl))
                        # pdb.set_trace()
                    fout.write(u'{}\r\n'.format(sl))
                    outputLineCount += 1

    fout.close()
    print('=== Output Line Count: {} ==='.format(outputLineCount))

    
def main(dataFolderPattern, OutputPath, IntermediateFolder):
    
    destFolder1 = os.path.join(IntermediateFolder, '{}_A'.format(int(time.time())))
    destFolder2 = os.path.join(IntermediateFolder, '{}_B'.format(int(time.time())))
    os.mkdir(destFolder1)
    os.mkdir(destFolder2)
    ProcessStats(dataFolderPattern, destFolder1)
    # FilterNoNews('./training/filter20180323a/')
    FilterLines(destFolder1, destFolder2)
    # CountLines('./training/filter20180324c/')
    #SplitLines(destFolder2, OutputPath)
    MergeRawText(destFolder2, OutputPath)



if __name__ == '__main__':
    # dataFolderPattern = '/Users/AlexG/majorwork/bbcData/2018*'
    dataFolderPattern = sys.argv[1]
    OutputPath = sys.argv[2]
    IntermediateFolder = sys.argv[3]
    main(dataFolderPattern, OutputPath, IntermediateFolder)

            

