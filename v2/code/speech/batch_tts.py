#encoding:utf8
from text_to_speech_converter import Text2SpeechConverter, sha
from util import loadLines
import time
import os

def batchTts(save_folder):
    lines = loadLines()
    N = len(lines)
    print('== Total {} =='.format(len(lines)))

    text2speech = Text2SpeechConverter('', '') 
    text2speech.getToken()
    
    ind = N
    error_count = 0
    for en, zh in lines:
        print('{} lines left.'.format(ind))
        ind -= 1

        # Format output path
        name = sha(en.decode('utf8'))
        output_path = save_folder + name + '.mp3'
        if os.path.exists(output_path):
            continue
        #print(output_path)
        content = text2speech.convert(en, outputPath = output_path)
        if content is None:
            error_count += 1
        time.sleep(5.5)
    print('Error count: {}'.format(error_count))
        
    
def main():
    save_folder = '/Users/AlexG/Documents/2019/E-Dream/2019.03/voices/'
    batchTts(save_folder)

if __name__ == '__main__':
    main()
