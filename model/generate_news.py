import gpt_2_simple as gpt2
import tensorflow as tf
from tensorflow.core.protobuf import rewriter_config_pb2
import os, sys, re, json
import argparse
current_file_path = os.path.abspath(__file__)
print('current file path:', current_file_path)
sys.path.append(os.path.join(os.path.dirname(current_file_path), '..', 'util'))
from util.checkSentenceDuplicate import SentenceDuplicateDetector

model_name = "117M"
print('Using cached model 117M')

def judgeScriptLength(line, min_len = 5):
    return len(line.split(' ')) > min_len

endingPattern = re.compile(r'[^a-z0-9A-Z]$')
def judgeEnding(line):
    return endingPattern.search(line) != None

def splitLine(line):
    quotes = [
        u'""',
        u'“”'
    ]
    stops = set([
        '.',
        ',',
        '，',
        '。',
        '!',
        '?',
        ';'
        ])
    results = []
    cur = ''
    prev_quote = None
    for c in line:
        ch = c
        if prev_quote is not None:
            if c == quotes[prev_quote][1] and judgeScriptLength(cur.strip(' ')):
                cur += c
                results.append(cur.strip(' '))
                cur = ''
                prev_quote = None
                ch = ''
        else:
            if c in stops and judgeScriptLength(cur.strip(' ')):
                cur += c 
                results.append(cur.strip(' '))
                cur = ''
                ch = ''
            
        cur += ch
        for ind in range(len(quotes)):
            if quotes[ind][0] == ch:
                prev_quote = ind
                break
    if judgeScriptLength(cur.strip(' ')):
        results.append(cur.strip(' '))
    return results

def scriptFilter(line):
    nameSet = set(['he',
        'she',
        'who',
        'say',
        'said',
        'says',
        'tell',
        'tells',
        'my',
        'me',
        'his',
        'her',
        'them',
        'they',
        'ours',
        'our',
        'us',
        'jack',
        'rose',
        'you'
    ])
    patterns = []
    for n in nameSet:
        pat = re.compile(r'\b{}\b'.format(n))
        patterns.append(pat)
    rows = line.split('\n')
    results = []
    for r in rows:
        rl = r.lower()
        for w in nameSet:
            if pat.search(rl) != None and judgeScriptLength(rl):
                results.append(r)
                break
    return results

def randomStory(sess, prefix, turn = 100, length = 1023):
    lineSet = set()
    cur = prefix
    story = []
    for ind in range(turn):
        print('story turn ', ind)
        print('prefix:', cur)
        results = gpt2.generate(sess,
        length=length,
        nsamples=20,
        temperature=0.7,
        prefix=cur,
        return_as_list=True)

        next_line = None
        for line in results:
            if line not in lineSet and judgeEnding(line) and judgeScriptLength(line):
                next_line = line
                lineSet.add(line)
                break
        # Add valid line to story
        if next_line is not None:
            split_results = splitLine(next_line)
            if len(split_results) > 0:
                min_l = split_results[-1]
                for l in split_results[::-1]:
                    if len(l) < len(min_l):
                        min_l = l
                cur = min_l
            for l in split_results:
                if l not in lineSet and judgeEnding(l) and judgeScriptLength(l):
                    story.append(l)
                    lineSet.add(l)
        print('='*20)
        print('\n'.join(story))

    return story

def parseInputPrefix(prev_file):
    print('reading previous lines from', prev_file)
    input_prefix = None
    with open(prev_file, 'r', encoding='utf8') as fin:
        for line in fin:
            content = line.strip(' \r\n')
            content_words = len(content.split(' '))
            if content_words >= 5 and content_words < 15:
                input_prefix = content
    return input_prefix

def prepareDetector(dream_json_path):
    with open(dream_json_path, 'r', encoding='utf8') as fin:
        data = json.load(fin)
    detector = SentenceDuplicateDetector()
    for en, zh, h in data:
        detector.ingest(en)
    return detector

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-output_file', nargs=1, help='output file')
    parser.add_argument('-dream_json_path', nargs=1, help='path to current dream.json, which contains all the generated lines')
    parser.add_argument('-previous_story_file', nargs=1, help='previous file to search for story prefix')
    parser.add_argument('-min_story_lines', nargs=1, type=int, default=10, help='previous file to search for story prefix')
    parser.add_argument('-max_story_lines', nargs=1, type=int, default=80, help='previous file to search for story prefix')
    args = vars(parser.parse_args())
    print('args:', args)
    output_file = args['output_file'][0]
    min_story_lines = args['min_story_lines']
    max_story_lines = args['max_story_lines']

    print('output file: {}'.format(output_file))
    input_prefix = 'She looks at the president,'
    if args['previous_story_file'] is not None:
        input_prefix = parseInputPrefix(args['previous_story_file'][0])
    print('Input prefix: ', input_prefix)
    
    detector = prepareDetector(args['dream_json_path'][0])
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess)
    story = []
    while len(story) < min_story_lines:
        for line in randomStory(sess, input_prefix, turn=3, length = 150):
            if detector.isDuplicateBrute(line):
                continue
            else:
                detector.ingest(line)
                story.append(line)
    with open(output_file, 'w', encoding='utf8') as fout:
        for line in story:
            fout.write(line)
            fout.write('\n')
