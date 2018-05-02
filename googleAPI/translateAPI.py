#encoding:utf8

# Imports the Google Cloud client library
from google.cloud import translate


def TranslateChinese(text, target = 'zh-CN'):
    '''language:
        zh-CN
        en
    '''
    # Instantiates a client
    translate_client = translate.Client()

    # The text to translate
    # text = u'Hello, world!'
    # The target language
    # target = 'zh-CN'

    # Translates some text into Russian
    translation = translate_client.translate(
        text,
        target_language=target)

    # print(u'Text: {}'.format(text))
    # print(u'Translation: {}'.format(translation['translatedText']))
    return translation['translatedText']



