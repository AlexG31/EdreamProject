#encoding:utf8
from Text2SpeechConverter import Text2SpeechConverter
import time
import json, codecs
import os, sys

def batchTts(lines, save_folder, private_key):
    N = len(lines)
    print('== Total {} lines =='.format(N))

    text2speech = Text2SpeechConverter('', '', private_key = private_key) 
    text2speech.getToken()
    
    ind = N
    error_count = 0
    for en, zh, en_hash in lines:
        print('{} lines left.'.format(ind))
        ind -= 1

        # Format output path
        name = en_hash
        output_path = save_folder + name + '.mp3'
        if os.path.exists(output_path):
            continue
        #print(output_path)
        content = text2speech.convert(en, outputPath = output_path)
        if content is None:
            error_count += 1
        time.sleep(5.5)
    print('Error count: {}'.format(error_count))
        

def loadLines(in_path):
    with codecs.open(in_path, 'r', 'utf8') as fin:
        data = json.load(fin)

    return data

def getPrivateKey():
    if 'TTS_PRIVATE_KEY' in os.environ:
        subscriptionKey = os.environ['TTS_PRIVATE_KEY']
        return subscriptionKey
    else:
        print('Environment variable for TRANSLATOR_TEXT_KEY is not set.')
        exit()
    
def main():
    in_file = sys.argv[1]
    save_folder = sys.argv[2]
    private_key = getPrivateKey()

    lines = loadLines(in_file)
    batchTts(lines, save_folder, private_key)

if __name__ == '__main__':
    main()
