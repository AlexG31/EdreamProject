#encoding:utf8
import csv, codecs


def loadLines(in_path = r'/Users/AlexG/Documents/2019/E-Dream/2019.03/lines/clean-lines.csv'):
    lines = []
    with codecs.open(in_path, 'r', encoding = 'utf8') as fin:
        csv_reader = csv.reader(utf_8_encoder(fin))
        for row in csv_reader:
            if row is None or len(row) == 0 or len(row[0]) == 0:
                print('Error! empty row: [{}]'.format(row))
                continue
            lines.append(row)
    return lines

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')
          
