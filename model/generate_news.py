import gpt_2_simple as gpt2
import tensorflow as tf
from tensorflow.core.protobuf import rewriter_config_pb2
import os, sys, re
model_name = "117M"
arg_length = len(sys.argv)
output_file = sys.argv[1]
input_prefix = 'She looks at the president,'
if arg_length > 2:
    prev_file = sys.argv[2]
    print('reading previous lines from', prev_file)
    with open(prev_file, 'r') as fin:
        for line in fin:
            content = line.strip(' \r\n')
            content_words = content.split(' ')
            if content_words >= 5 and content_words < 15:
                input_prefix = content
print('Input prefix: ', input_prefix)
print('output file: {}'.format(output_file))
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

if __name__ == '__main__':
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess)
    story = randomStory(sess, input_prefix, turn=3)
    with open(output_file, 'w', encoding='utf8') as fout:
        for line in story:
            fout.write(line)
            fout.write('\n')