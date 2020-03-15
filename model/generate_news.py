import gpt_2_simple as gpt2
import tensorflow as tf
from tensorflow.core.protobuf import rewriter_config_pb2
import os, sys, re, json, random
import argparse
import pdb
import codecs
current_file_path = os.path.abspath(__file__)
print('current file path:', current_file_path)
sys.path.append(os.path.join(os.path.dirname(current_file_path), '..', 'util'))
from checkSentenceDuplicate import SentenceDuplicateDetector
from decode_shortplain_lines import manualStoryRules

model_name = "117M"
print('Using cached model 117M')

fix_seeds = ["Jack and Rose ",
"Jack and Rose ",
"Jack told Rose, ",
"Rose told Jack, ",
"Looking at her ",
"Looking at him ",
"Sitting next to each other ",
"Suddenly ",
"All of a sudden ",
"Then ",
"Afterwards ",
"After a while ",
"The other day ",
"In the end ",
"Finally ",
"Eventually ",
"Soon ",
"As soon as ",
"Once again ",
"Once upon a time ",
"Later ",
"Still ",
"At this moment ",
"For a moment ",
"Meanwhile ",
"At the same time ",
"One day after ",
"One day before ",
"One day ",
"Year after year ",
"Day by day ",
"As time passed by ",
"Last summer ",
"Last night ",
"In spring ",
"On the day ",
"For many times ",
"Every time ",
"However ",
"Moreover ",
"Besides ",
"At last ",
"Last ",
"On ",
"In ",
"At ",
"Once ",
"Before ",
"After "]
def judgeScriptLength(line, min_len = 5):
    return len(line.split(' ')) > min_len

endingPattern = re.compile(r'[^a-z0-9A-Z]$')
def judgeEnding(line):
    return endingPattern.search(line) != None

def removeEmptyLines(lines):
    res = []
    for l in lines:
        l = l.strip(' \r\n')
        l = l.replace('\r', ' ')
        l = l.replace('\n', ' ')
        if len(l) > 0 and judgeEnding(l) and judgeScriptLength(l):
            res.append(l)
    return res

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
    must_have_space_tail_stops = ['.', ',']
    results = []
    cur = ''
    prev_quote = None
    n = len(line)
    for char_ind, c in enumerate(line):
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
                if c in must_have_space_tail_stops:
                    if char_ind + 1 < n and line[char_ind + 1] == ' ':
                        results.append(cur.strip(' '))
                        cur = ''
                        ch = ''
                else:
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

def randomStory(sess, prefix, previous_line_count, args, raw_story, turn = 100, length = 1023):
    lineSet = set()
    cur = prefix
    story = []
    for ind in range(turn):
        print('story turn ', ind)
        print('prefix:', cur)
        if (ind + previous_line_count) % args['fix_seed_period'] == 0:
            manual_seed = fix_seeds[random.randint(0, len(fix_seeds) - 1)]
            cur = manual_seed
        results = gpt2.generate(sess,
        length=length,
        nsamples=20,
        temperature=0.7,
        prefix=cur,
        return_as_list=True)

        next_line = None
        for line in results:
            raw_story.append(line)
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

def countDreamJson(dream_json_path):
    with open(dream_json_path, 'r', encoding='utf8') as fin:
        data = json.load(fin)
    print('total number of lines in dream json: {}'.format(len(data)))
    return len(data)

# Replace jack/rose
replaceMap = [
    (re.compile(r"\b[Ss]he\b"), "Rose"),
    (re.compile(r"\b[Hh]er\b"), "Rose"),
    (re.compile(r"\b[Hh]e\b"), "Jack"),
    (re.compile(r"\b[Hh]im\b"), "Jack"),
]
def randomReplaceJackRose(line, replace_proba = 0.8):
    replace_count = 0
    src = line
    for pat, token in replaceMap:
        search_result = pat.search(src)
        if search_result is not None:
            if random.random() <= replace_proba:
                src = src[:search_result.start()] + token + src[search_result.end():]
                replace_count += 1

    if replace_count > 0:
        print('Total replace jack/rose:', replace_count)
    return src

def readTmp(path):
    res = []
    with codecs.open(path, 'r', 'utf8') as fin:
        for line in fin:
            res.append(line)

    return res

def main(args):
    output_file = args['output_file'][0]
    raw_output_file = args['raw_output_file'][0]
    min_story_lines = args['min_story_lines']
    max_story_lines = args['max_story_lines']
    max_gen = args['max_generate_iteration']

    print('output file: {}'.format(output_file))
    input_prefix = 'She looks at the president,'
    if args['previous_story_file'] is not None:
        input_prefix = parseInputPrefix(args['previous_story_file'][0])
    print('Input prefix: ', input_prefix)
    
    total_dream_lines = countDreamJson(args['dream_json_path'][0])
    detector = prepareDetector(args['dream_json_path'][0])
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess)
    story = []
    raw_story = []
    gen_count = 0
    while len(story) < min_story_lines:
        gen_count += 1
        if gen_count > max_gen:
            break
        rs = randomStory(sess, input_prefix, total_dream_lines, args, raw_story, turn=1, length = 150)
        rs = removeEmptyLines(rs)
        for line in rs:
            line = randomReplaceJackRose(line)
            if detector.isDuplicateBrute(line):
                continue
            else:
                detector.ingest(line)
                story.append(line)
    story = story[:max_story_lines]
    story = manualStoryRules(story)
    with open(output_file, 'w', encoding='utf8') as fout:
        for line in story:
            fout.write(line)
            fout.write('\n')
    with open(raw_output_file, 'w', encoding='utf8') as fout:
        for line in raw_story:
            fout.write(line)
            fout.write('\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-output_file', nargs=1, help='output file')
    parser.add_argument('-raw_output_file', nargs=1, help='raw model output')
    parser.add_argument('-dream_json_path', nargs=1, help='path to current dream.json, which contains all the generated lines')
    parser.add_argument('-previous_story_file', nargs=1, help='previous file to search for story prefix')
    parser.add_argument('-min_story_lines', nargs=1, type=int, default=10, help='previous file to search for story prefix')
    parser.add_argument('-max_story_lines', nargs=1, type=int, default=80, help='previous file to search for story prefix')
    parser.add_argument('-max_generate_iteration', nargs=1, type=int, default=30, help='previous file to search for story prefix')
    parser.add_argument('-fix_seed_period', type=int, default=100, help='fix replace period of manual seed')
    args = vars(parser.parse_args())
    print('args:', args)
    main(args)